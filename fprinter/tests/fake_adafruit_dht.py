AM2302 = 'AM2302'


def read_retry(model, pin):
    print('fake_adafruit_dht.read_retry - {}'.format((model, pin)))
    return 0.5, 28
