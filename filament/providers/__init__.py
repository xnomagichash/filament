import ConfigParser


class Provider(type):
    _providers = {}

    def __new__(cls, clsname, bases, dct):
        newcls =  super(Provider, cls).__new__(cls, clsname, bases, dct)
        cls._providers[dct['name']] = newcls
        return newcls

    @classmethod
    def load(cls, fp, section=None):
        with open(fp) as providerf:
            rcp = ConfigParser.RawConfigParser()
            rcp.readfp(providerf)
            if section:
                return cls._providers[section].create(rcp)
            for provider_name, provider in cls._providers.iteritems():
                if rcp.has_section(provider_name):
                    return provider(rcp)
            else:
                raise Exception("bad provider")

    def ready(self):
        pass

    def wait(self):
        pass


# providers

from . import digitalocean
