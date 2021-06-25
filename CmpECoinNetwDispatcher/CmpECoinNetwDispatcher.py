#!/usr/bin/env python
import pika, sys, os, threading
from transxRcvQ import transxRcvQ
from validatedBlockRcvQ import validatedBlockRcvQ

try:
	transxRcvQ_ = transxRcvQ()
	validatedBlockRcvQ_ = validatedBlockRcvQ()

	transxRcvQ_.start()
	validatedBlockRcvQ_.start()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
