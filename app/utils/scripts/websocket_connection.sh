#!/usr/bin/bash

wscat -c ws://localhost:3000/ws/wsinit \ \
  -H "Authorization: Bearer <TOKEN>"