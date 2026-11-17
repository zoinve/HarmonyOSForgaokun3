"""Connect reference commands to upstream P2P; never synthesize link events."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
UPSTREAM = 'd945ddd368085f255e68328f2d3b020ceea359af'

WRAPPER = r'''
#include "share-magiclink-497.h"
static int share497_magiclink(struct wpa_supplicant *wpa_s, char *text)
{
    struct share497_request request;
    struct wpa_config *temporary;
    struct wpa_ssid *ssid;
    u8 bssid[ETH_ALEN];
    int result = -1;
    if (!wpa_s->global->p2p || wpa_s->global->p2p_disabled ||
        wpa_s->global->p2p_group_formation || share497_parse(text, &request) ||
        hwaddr_aton(request.bssid, bssid) || is_zero_ether_addr(bssid) ||
        (bssid[0] & 1))
        return -1;
    temporary = wpa_config_alloc_empty(NULL, NULL);
    if (!temporary) return -1;
    ssid = wpa_config_add_network(temporary);
    if (!ssid) goto done;
    wpa_config_set_network_defaults(ssid);
    if (wpa_config_set(ssid, "ssid", request.ssid_hex, 0) < 0 ||
        wpa_config_set(ssid, "psk", request.key, 0) < 0)
        goto done;
    if (ssid->passphrase) wpa_config_update_psk(ssid);
    if (!ssid->psk_set) goto done;
    ssid->disabled = 2;
    ssid->mode = WPAS_MODE_INFRA;
    ssid->p2p_group = 1;
    ssid->p2p_persistent_group = 1;
    os_memcpy(ssid->bssid, bssid, ETH_ALEN);
    /* Upstream copies the credentials into a temporary group network, selects
     * that network and runs its normal scan, association and WPA handshake. */
    result = wpas_p2p_group_add_persistent(wpa_s, ssid, 0, 0,
        request.frequency, 0, 0, 0, 0, 0, 0, NULL, 0, 1, false, 0, bssid);
done:
    wpa_config_free(temporary);
    return result;
}
'''


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


def control(source):
    anchor = 'char * wpa_supplicant_ctrl_iface_process(struct wpa_supplicant *wpa_s,'
    source = once(source, anchor, '#ifdef CONFIG_P2P\n' + WRAPPER + '\n#endif\n' + anchor)
    anchor = '\tif (os_strncmp(buf, WPA_CTRL_RSP, os_strlen(WPA_CTRL_RSP)) == 0 ||'
    source = once(source, anchor,
        '\tif (os_strncmp(buf, "MAGICLINK ", 10) == 0) {\n'
        '\t\twpa_dbg(wpa_s, MSG_DEBUG, "Control interface command MAGICLINK [REMOVED]");\n'
        '\t} else ' + anchor.lstrip())
    anchor = '\t} else if (os_strcmp(buf, "P2P_GROUP_ADD") == 0) {'
    source = once(source, anchor,
        '\t} else if (os_strncmp(buf, "MAGICLINK ", 10) == 0) {\n'
        '\t\tif (share497_magiclink(wpa_s, buf + 10))\n'
        '\t\t\treply_len = -1;\n' + anchor)
    return source


def driver(source):
    anchor = '\tif (os_strstr(param, "use_p2p_group_interface=1")) {'
    return once(source, anchor,
        '\t/* The original bridge requires a real netdev for SIOCGIFHWADDR. */\n'
        '\tif (os_strstr(param, "use_p2p_netdev=1"))\n'
        '\t\tdrv->capa.flags &= ~WPA_DRIVER_FLAGS_DEDICATED_P2P_DEVICE;\n' + anchor)
