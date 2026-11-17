#ifndef NATIVE_AUDIO_PROTOCOL_412_H
#define NATIVE_AUDIO_PROTOCOL_412_H
#include "native-audio-protocol-315.h"

/* Additive v2 routes; old servers reject these instead of returning silence. */
#define AUDIO412_MIC 2U
#define AUDIO412_HEADSET_MIC 3U
#define AUDIO412_READ 6U
/* Capture: submitted=delivered frames, played=delivered+hardware available.
 * READ reply header is followed by exactly accepted_bytes real PCM bytes. */
#endif
