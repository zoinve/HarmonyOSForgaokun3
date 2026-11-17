# Experiment 090: genuine network state refresh after guide registration

089 proves first guide receives validated network capability 16, while a
replacement guide sees a default network but times out without the capability
callback. Both original HTTP/HTTPS probes independently returned 204. This
supports testing an actual network transition after registration, not fabricated
validation events or another force-stop attempt.

Reuse byte-identical core 087, original services/permissions/packages, real WPA
credentials, original NetManager/DHCP bridge, and 088 canonical workspace mount.
Only the existing owned diagnostic shell script changes. No private code patch,
provisioning edit, certificate bypass, synthetic network event or guide stop.

At uptime 100 require one SceneBoard PID surviving another ten seconds and an
existing guide. Require the real control socket and a successful original
wpa_cli status containing exactly wpa_state=COMPLETED. Request disconnect once,
wait three seconds, observe status and request reconnect once regardless of the
disconnect return status. Record final states at uptime 120/135. No repeat cycle
or command retries. The original supplicant retains the existing private real
profile; this script never opens, exports or changes it.

Success for this hypothesis requires original service/OOBE callbacks correlated
with the actual WPA transition. Neither wpa_cli exit zero nor association alone
proves validation, OOBE completion, activation or an interactive native desktop.
The full goal remains unchanged; original CollaborationFwk query latency is a
separate outstanding cause of SceneBoard failure.

Preserve Ubuntu default, bounded return, screen-off timer, original images,
firmware/manual entry and shared payloads. Retain entries 089/090, archive 088.
Retrieval must exclude all three previous raw-prefix-087 runs. Retrieve evidence
before running preservation verification, never mount the partition concurrently.
