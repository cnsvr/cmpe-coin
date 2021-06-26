from validator import CmpECoinValidatorNode

try:
    CmpECoinValidatorNode()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)