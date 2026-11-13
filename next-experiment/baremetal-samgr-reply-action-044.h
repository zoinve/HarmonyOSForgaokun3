/* No remote response/dead manager may be retried; a real rejection must not be hidden. */
static int samgr_reply_action_044(int received, int actual_reply, int status)
{
    if (!received || !actual_reply) return 0;
    return status == 0 ? 1 : -1;
}
