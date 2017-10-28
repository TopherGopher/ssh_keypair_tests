#!/usr/local/bin/python

# https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA-module.html

from cryptography.hazmat.backends import default_backend \
    as crypto_default_backend
from cryptography.hazmat.primitives import serialization \
    as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from hashlib import sha1
from logging import DEBUG
from logging import Formatter
from logging import StreamHandler
from logging import getLogger
from subprocess import PIPE
from subprocess import Popen
from sys import stdout


class KeyPairGenerator():
    """
    Args:
        target (str): Target can be cloud or disk
    """
    def __init__(self, target="cloud", folder_id=None, store_it=None):
        # Initialize a logger for readable/debuggable STDOUT
        self.init_logger()

        if target == "cloud":
            self.fit = store_it
            # Oh you should be using sub classes! Bite me.
            self.write_keys = self.write_keys_to_cloud
        elif target == "disk":
            self.write_keys = self.write_keys_to_disk
        else:
            raise Exception("'disk' and 'cloud' are the only accepted " +
                            "values. Not {0}!".format(self.target))
        self.target = target

        self.folder_id = folder_id

    def init_logger(self):
        self.logger = getLogger(__name__)
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() PID %(process)d] %(message)s"
        self.logger.setLevel(DEBUG)
        ch = StreamHandler(stdout)
        ch.setLevel(DEBUG)
        ch.setFormatter(Formatter(FORMAT))
        self.logger.addHandler(ch)

    def check_entropy(self):
        # Blatantly stolen from ttps://stackoverflow.com/q/5480131/679458
        arg = ['cat', '/proc/sys/kernel/random/entropy_avail']
        ps = Popen(arg, stdout=PIPE)
        return int(ps.communicate()[0])

    def get_key_hash(self, key):
        return sha1(key.encode('UTF-8')).hexdigest()

    def generate_key_pairs(self):
        # Using cryptography because pycrypto hasn't been maintained since 2014
        # See latest commit :-( https://github.com/dlitz/pycrypto
        # Terrifying to use nonetheless because of the warning at the top

        # TODO: Figure out cryptography source...urandom?
        # Using os.urandom() to source /dev/urandom as upstream
        # Per https://stackoverflow.com/q/5480131/679458

        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption())
        public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        )

        # Decoding the secrets? Already? Scandelous.
        return private_key.decode('UTF-8'), public_key.decode('UTF-8')

    def write_keys_to_disk(self, key_hash, private_key, public_key):
        with open("{0}.key".format(key_hash), 'w') as priv_fp, \
                open("{0}.pub".format(key_hash), 'w') as pub_fp:
            priv_fp.write(private_key)
            pub_fp.write(public_key)

    def write_keys_to_cloud(self, key_hash, private_key, public_key):
        self.fit.create_file(fname="{0}.key".format(key_hash),
                             folder_id=self.folder_id,
                             body=private_key)

        self.fit.create_file(fname="{0}.pub".format(key_hash),
                             folder_id=self.folder_id,
                             body=public_key)

    def write_key_pairs(self):
        self.logger.info("Generating keypair. Entropy: {ent}".format(
            ent=self.check_entropy()))
        private_key, public_key = self.generate_key_pairs()

        key_hash = self.get_key_hash(private_key)

        self.write_keys(key_hash, private_key, public_key)

        self.logger.info("Created keypair {0}.(key|pub)".format(key_hash))

        return key_hash


if __name__ == '__main__':
    kpg = KeyPairGenerator()
    kpg.write_key_pairs()
