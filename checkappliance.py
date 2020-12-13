import hassapi as hass
import requests
import json
import codecs
from datetime import datetime

appliance_ip = '?.?.?.?'                    # The IP address of the appliance
appliance_entity = 'sensor.tumble_dryer'    # The name of the entity to use/create in Home Assistant (the stats use the same value with '_stats' appended)
status_root = 'statusTD'                    # The root level JSON element returned by 'http-read'
power_attribute = 'StatoTD'                 # The name of the JSON attribute that containes the power on/off state.
stats_root = 'statusCounters'               # The root level JSON element returned by 'http-getStatistics'
primary_statistic = 's3'                    # The name of the JSON attribute that containes the 'main' statisict (e.g. s3 appears to be number of cycles).
encryption_key = 'XXXXXXXXXXXXXXXX'         # The encryption key obtained from your appliance
polling_interval = 15                       # How frequently check for the latest status.

class CheckAppliance(hass.Hass):
    def initialize(self):
        self.run_every(self.check_appliance, datetime.now(), polling_interval)

    def check_appliance(self, kwargs):
        try:
            status = self.get_status()
            self.set_state(appliance_entity, state = 'on' if status[status_root][power_attribute] == '2' else 'off', attributes = status[status_root])
        except:
            self.set_state(appliance_entity, state = 'unavailable')
        
        try:
            stats = self.get_stats()
            self.set_state(appliance_entity + '_stats', state = stats[stats_root][primary_statistic], attributes = stats[stats_root])
        except:
            pass

    def get_status(self):
        return self.get_data('read')

    def get_stats(self):
        return self.get_data('getStatistics')

    def get_data(self, command):
        res = requests.get('http://' + appliance_ip + '/http-' + command + '.json?encrypted=1')

        return json.loads(self.decrypt(codecs.decode(res.text, 'hex'), encryption_key))

    def decrypt(self, cipher_text, key):
        decrypted = ''

        for i in range(len(cipher_text)):
            decrypted += chr(cipher_text[i] ^ ord(key[i % len(key)]))

        return decrypted