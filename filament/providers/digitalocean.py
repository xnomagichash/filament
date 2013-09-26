import requests
import time
from . import Provider
from fabric import api

class Droplet(object):
    __metaclass__ = Provider
    host = "https://api.digitalocean.com"
    name = 'Digital Ocean'

    @property
    def _params(self):
        return {'api_key': self.api_key, 'client_id': self.client_id}

    def __init__(self, config):
        self._ssh_keys = []
        g = lambda x: config.get('Digital Ocean', x)
        self.api_key   = g('api_key')
        self.client_id = g('client_id')
        self.size      = g('size')
        self.image     = g('image')
        self.region    = g('region')
        self.ssh_keys  = g('ssh_keys')

    def create(self):
        url = "{0}/droplets/new".format(self.host)
        keylist = ",".join(map(str,self._ssh_keys))
        try:
            r = requests.get(url, params={
                "name": self.name,
                "api_key": self.api_key,
                "size_id": self.size_id,
                "image_id": self.image_id,
                "client_id": self.client_id,
                "region_id": self.region_id,
                "ssh_key_ids": keylist,
                "private_networking": "true"
            })
        except AttributeError:
            raise
        else:
            self.id = r.json()['droplet']['id']
            return self

    @property
    def ready(self):
        url = "{0}/droplets/{1}".format(self.host, self.id)
        try:
            r = requests.get(url,params=self._params)
        except AttributeError:
            raise
        else:
            try:
                data = r.json()['droplet']
            except:
                return False
            else:
                for k,v in data.iteritems():
                    setattr(self, k, v)
                return data['status'] == 'active'


    @property
    def regions(self):
        try:
            return self._regions
        except:
            url = "{0}/regions".format(self.host)
            regions = requests.get(url,params=self._params).json()['regions']
            self._regions = {region['slug']: region['id'] for region in regions}
            return self._regions

    def _sregion(self, region):
        self.region_id = self.regions[region.lower()]

    def _gregion(self):
        return {k:v for v,k in self.regions.items()}[self.region_id]

    region = property(_gregion, _sregion)


    @property
    def sizes(self):
        try:
            return self._sizes
        except:
            url = "{0}/sizes".format(self.host)
            sizes = requests.get(url,params=self._params).json()['sizes']
            self._sizes = {size['name'].upper(): size['id'] for size in sizes}
            return self._sizes

    def _ssize(self, size):
        self.size_id = self.sizes[size.upper()]

    def _gsize(self):
        return {k:v for v,k in self.sizes.items()}[self.size_id]

    size = property(_gsize, _ssize)


    @property
    def images(self):
        try:
            return self._images
        except:
            url = "{0}/images".format(self.host)
            images = requests.get(url,params=self._params).json()['images']
            self._images = {image['name']: image['id'] for image in images}
            return self._images

    def _simage(self, image):
        self.image_id = self.images[image]

    def _gimage(self):
        return {k:v for v,k in self.images.items()}[self.image_id]

    image = property(_gimage, _simage)


    @property
    def available_ssh_keys(self):
        try:
            return self._available_ssh_keys
        except:
            url = "{0}/ssh_keys".format(self.host)
            ssh_keys = requests.get(url,params=self._params).json()['ssh_keys']
            kd = {ssh_key['name']: ssh_key['id'] for ssh_key in ssh_keys}
            self._available_ssh_keys = kd
            return kd

    def _sssh_keys(self, ssh_keys):
        if type(ssh_keys) is not list:
            ssh_keys = [ssh_keys]
        self._ssh_keys = [self.available_ssh_keys[key] for key in ssh_keys]

    def _gssh_keys(self):
        kdict = {k:v for v,k in self.available_ssh_keys.items()}
        return [kdict[key] for key in self.ssh_keys]

    def _dssh_key(self, key):
        kdict = {k:v for v,k in self.available_ssh_keys.items()}
        self._ssh_keys.remove(kdict[key])

    ssh_keys = property(_gssh_keys, _sssh_keys, _dssh_key)

    def wait(self):
        while not self.ready:
            print("Droplet {0} not yet ready. Sleeping for 5 seconds...".format(self.id))
            time.sleep(5)
        else:
            wait_string = "Droplet {0} ready. Waiting {1} seconds to connect..."
            for x in range(30, 0, -10):
                print(wait_string.format(self.id, x))
                time.sleep(10)
            print("Droplet {0} ready. Connecting...".format(self.id))
        while True:
            try:
                api.run('apt-get update', quiet=True)
            except Exception:
                print("Droplet {0} could not connect...".format(self.id))
                print("Waiting 5 seconds before trying again...")
                time.sleep(5)
            else:
                break

        return self

