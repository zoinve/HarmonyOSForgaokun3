#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>
#include <libavcodec/avcodec.h>
#include <libavutil/error.h>
#include <libavutil/pixfmt.h>

/* Both deployed bridges use this ABI, including the response tail padding. */
#define MAGIC 0x3144564bU
#define INPUT_CAP (8U * 1024U * 1024U)
#define SLOT_CAP (16U * 1024U * 1024U)
#define RELEASE_FLAG 0x40000000U
struct request {
    uint32_t magic, version, op, channel, input_size, codec;
    uint64_t timestamp;
};
struct response {
    uint32_t magic, version;
    int32_t status;
    uint32_t consumed, width, height, stride, bit_depth;
    uint64_t timestamp;
    uint32_t y_offset, u_offset, v_offset, output_size;
    int32_t helper_error;
};
_Static_assert(sizeof(struct request) == 32, "request ABI");
_Static_assert(sizeof(struct response) == 64, "response ABI");
struct client {
    int fd, fds[2], release, draining, legacy;
    size_t output_cap;
    uint32_t locked;
    uint8_t *input, *output;
    AVCodecContext *codec;
    AVFrame *frame;
    AVPacket *packet;
};
static uid_t allowed_uid;
static int legacy_mode;

static int reply(int fd, struct response *r)
{
    return send(fd, r, sizeof(*r), MSG_NOSIGNAL) == sizeof(*r) ? 0 : -1;
}

static int receive_request(int fd, struct request *r, int fds[2], int create)
{
    char control[CMSG_SPACE(16 * sizeof(int))] = {0};
    struct iovec iov = {.iov_base = r, .iov_len = sizeof(*r)};
    struct msghdr msg = {.msg_iov = &iov, .msg_iovlen = 1,
        .msg_control = control, .msg_controllen = sizeof(control)};
    ssize_t n = recvmsg(fd, &msg, MSG_CMSG_CLOEXEC);
    int count = 0, valid = n == sizeof(*r) &&
        !(msg.msg_flags & (MSG_TRUNC | MSG_CTRUNC));
    for (struct cmsghdr *c = CMSG_FIRSTHDR(&msg); c;
         c = CMSG_NXTHDR(&msg, c)) {
        if (c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS ||
            c->cmsg_len < CMSG_LEN(0)) {
            valid = 0;
            continue;
        }
        size_t bytes = c->cmsg_len - CMSG_LEN(0);
        if (bytes % sizeof(int)) valid = 0;
        for (size_t i = 0; i < bytes / sizeof(int); ++i) {
            int received;
            memcpy(&received, (char *)CMSG_DATA(c) + i * sizeof(int), sizeof(int));
            if (create && count < 2) fds[count] = received;
            else close(received);
            ++count;
        }
    }
    return valid && count == (create ? 2 : 0) && r->magic == MAGIC &&
        r->version == 1 ? 0 : -1;
}

static int map_buffers(struct client *s)
{
    struct stat a, b;
    if (fstat(s->fds[0], &a) || fstat(s->fds[1], &b) ||
        !S_ISREG(a.st_mode) || !S_ISREG(b.st_mode) ||
        a.st_size < INPUT_CAP || b.st_size < (off_t)s->output_cap ||
        (a.st_dev == b.st_dev && a.st_ino == b.st_ino)) return -1;
    s->input = mmap(NULL, INPUT_CAP, PROT_READ, MAP_SHARED, s->fds[0], 0);
    s->output = mmap(NULL, s->output_cap, PROT_READ | PROT_WRITE,
        MAP_SHARED, s->fds[1], 0);
    return s->input == MAP_FAILED || s->output == MAP_FAILED ? -1 : 0;
}

static int free_slot(struct client *s)
{
    for (int i = 0; i < (s->release ? 4 : 1); ++i)
        if (!(s->locked & (1U << i))) return i;
    return -1;
}

static void output_frame(struct client *s, struct response *r)
{
    int slot = free_slot(s);
    if (slot < 0) {
        r->status = 1;
        r->helper_error = AVERROR(EAGAIN);
        return;
    }
    int rc = avcodec_receive_frame(s->codec, s->frame);
    if (rc) {
        r->status = rc == AVERROR(EAGAIN) || rc == AVERROR_EOF ? 1 : -1;
        r->helper_error = rc;
        return;
    }
    AVFrame *f = s->frame;
    uint64_t w = f->width > 0 ? (unsigned)f->width : 0;
    uint64_t h = f->height > 0 ? (unsigned)f->height : 0;
    uint64_t stride = (w + 63) & ~63ULL;
    uint64_t ch = (h + 1) / 2, cs = stride / 2;
    uint64_t total = stride * h + 2 * cs * ch;
    size_t capacity = s->release ? SLOT_CAP : s->output_cap;
    if (!w || !h || f->format != AV_PIX_FMT_YUV420P || total > capacity ||
        !f->data[0] || !f->data[1] || !f->data[2]) {
        r->status = -1;
        r->helper_error = AVERROR(ENOTSUP);
        av_frame_unref(f);
        return;
    }
    uint32_t offset = s->release ? (uint32_t)slot * SLOT_CAP : 0;
    r->y_offset = offset;
    r->u_offset = offset + stride * h;
    r->v_offset = r->u_offset + cs * ch;
    memset(s->output + offset, 0, total);
    for (int plane = 0; plane < 3; ++plane) {
        uint32_t start = plane == 0 ? r->y_offset : plane == 1 ? r->u_offset : r->v_offset;
        size_t rows = plane == 0 ? h : ch;
        size_t width = plane == 0 ? w : (w + 1) / 2;
        size_t pitch = plane == 0 ? stride : cs;
        for (size_t row = 0; row < rows; ++row)
            memcpy(s->output + start + row * pitch,
                f->data[plane] + (ptrdiff_t)row * f->linesize[plane], width);
    }
    r->status = 0;
    r->helper_error = 0;
    r->width = w; r->height = h; r->stride = stride;
    r->bit_depth = 8;
    r->output_size = total;
    r->timestamp = (uint64_t)f->pts;
    if (s->release) {
        s->locked |= 1U << slot;
        r->bit_depth |= 0x400U | ((uint32_t)slot << 16);
    }
    av_frame_unref(f);
}

static void decode(struct client *s, const struct request *q, struct response *r)
{
    if (q->input_size > INPUT_CAP || s->draining) {
        r->helper_error = AVERROR(EINVAL);
        return;
    }
    if (free_slot(s) < 0) {
        r->status = 1; r->helper_error = AVERROR(EAGAIN);
        return;
    }
    if (!q->input_size) { output_frame(s, r); return; }
    av_packet_unref(s->packet);
    int rc = av_new_packet(s->packet, q->input_size);
    if (rc < 0) { r->helper_error = rc; return; }
    /* Own a padded packet: the peer may reuse its shared input after reply. */
    memcpy(s->packet->data, s->input, q->input_size);
    s->packet->pts = (int64_t)q->timestamp;
    s->packet->dts = AV_NOPTS_VALUE;
    rc = avcodec_send_packet(s->codec, s->packet);
    av_packet_unref(s->packet);
    if (rc == AVERROR(EAGAIN)) {
        output_frame(s, r);
        return;
    }
    if (rc < 0) { r->helper_error = rc; return; }
    r->consumed = q->input_size;
    output_frame(s, r);
}

static void *serve(void *arg)
{
    struct client s = {.fd = *(int *)arg, .fds = {-1, -1}, .legacy = legacy_mode};
    free(arg);
    struct request q = {0};
    struct response r = {.magic = MAGIC, .version = 1, .status = -1};
    s.output_cap = (s.legacy ? 32U : 64U) * 1024U * 1024U;
    if (receive_request(s.fd, &q, s.fds, 1) || q.op != 1 || q.input_size ||
        (s.legacy ? q.codec != 0 : (q.codec & ~(RELEASE_FLAG | 0x80000000U | 1U)))) goto out;
    s.release = !s.legacy && !!(q.codec & RELEASE_FLAG);
    const AVCodec *codec = avcodec_find_decoder_by_name((q.codec & 0xffffU) == 1 ? "h264" : "hevc");
    s.codec = avcodec_alloc_context3(codec);
    s.frame = av_frame_alloc(); s.packet = av_packet_alloc();
    if (!codec || !s.codec || !s.frame || !s.packet || map_buffers(&s)) goto fail_create;
    s.codec->thread_count = 2;
    s.codec->thread_type = FF_THREAD_FRAME | FF_THREAD_SLICE;
    int rc = avcodec_open2(s.codec, codec, NULL);
    if (rc < 0) { r.helper_error = rc; goto fail_create; }
    r.status = 1;
    if (reply(s.fd, &r)) goto out;
    for (;;) {
        if (receive_request(s.fd, &q, s.fds, 0)) break;
        memset(&r, 0, sizeof(r));
        r.magic = MAGIC; r.version = 1; r.status = -1;
        r.helper_error = AVERROR(EINVAL);
        if (q.op == 2) decode(&s, &q, &r);
        else if (q.op == 3 && !q.input_size) {
            if (free_slot(&s) < 0) {
                r.status = 1; r.helper_error = AVERROR(EAGAIN);
            } else {
                rc = s.draining ? 0 : avcodec_send_packet(s.codec, NULL);
                if (rc == 0 || rc == AVERROR_EOF) s.draining = 1;
                if (rc == 0 || rc == AVERROR_EOF || rc == AVERROR(EAGAIN)) output_frame(&s, &r);
                else r.helper_error = rc;
            }
        } else if (q.op == 5 && s.release && q.channel < 4 &&
                   (s.locked & (1U << q.channel)) && !q.input_size) {
            s.locked &= ~(1U << q.channel);
            r.status = 1; r.helper_error = 0;
        } else if (q.op == 4 && !q.input_size) {
            r.status = 1; r.helper_error = 0;
            reply(s.fd, &r); break;
        }
        if (reply(s.fd, &r)) break;
        if (r.status < 0) break;
    }
    goto out;
fail_create:
    if (!r.helper_error) r.helper_error = AVERROR(EINVAL);
    reply(s.fd, &r);
out:
    av_packet_free(&s.packet); av_frame_free(&s.frame); avcodec_free_context(&s.codec);
    if (s.input && s.input != MAP_FAILED) munmap(s.input, INPUT_CAP);
    if (s.output && s.output != MAP_FAILED) munmap(s.output, s.output_cap);
    for (int i = 0; i < 2; ++i) if (s.fds[i] >= 0) close(s.fds[i]);
    close(s.fd);
    return NULL;
}

int main(int argc, char **argv)
{
    if (argc != 4 || (strcmp(argv[2], "legacy") && strcmp(argv[2], "ring"))) return 2;
    char *end;
    errno = 0;
    unsigned long uid = strtoul(argv[3], &end, 10);
    if (errno || !*argv[3] || *end || uid > UINT32_MAX) return 2;
    allowed_uid = (uid_t)uid; legacy_mode = !strcmp(argv[2], "legacy");
    struct sockaddr_un address = {.sun_family = AF_UNIX};
    if (strlen(argv[1]) >= sizeof(address.sun_path)) return 2;
    strcpy(address.sun_path, argv[1]);
    /* Never unlink an arbitrary or live socket. Launcher owns stale cleanup. */
    int listener = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
    if (listener < 0 || bind(listener, (void *)&address, sizeof(address)) ||
        chmod(argv[1], 0666) || listen(listener, 8)) return 3;
    printf("SOFTWARE_CODEC_READY mode=%s uid=%u socket=%s\n", argv[2], (unsigned)allowed_uid, argv[1]);
    fflush(stdout);
    for (;;) {
        int fd = accept4(listener, NULL, NULL, SOCK_CLOEXEC);
        if (fd < 0) { if (errno == EINTR) continue; return 4; }
        struct ucred peer;
        socklen_t len = sizeof(peer);
        if (getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &peer, &len) ||
            len != sizeof(peer) || peer.uid != allowed_uid) { close(fd); continue; }
        struct timeval timeout = {.tv_sec = 30};
        setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
        setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
        int *arg = malloc(sizeof(*arg));
        if (!arg) { close(fd); continue; }
        *arg = fd;
        pthread_t thread;
        if (pthread_create(&thread, NULL, serve, arg)) { free(arg); close(fd); }
        else pthread_detach(thread);
    }
}
