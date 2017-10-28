import multiprocessing
from generate_key_pairs import KeyPairGenerator
from config import config
from storage import StoreIt
from os import remove
from time import sleep

key_count = multiprocessing.Value('i', 0)
key_q = multiprocessing.JoinableQueue()


def write_em(kpg, keys_per_worker):
    """
    I've beeen workin on the raaaail road.
    """
    global key_count
    for _ in range(keys_per_worker):
        key_q.put(kpg.write_key_pairs())
        with key_count.get_lock():
            key_count.value += 1
        kpg.logger.info("Generated {0} keys".format(key_count.value))
    return


def push_em(store_it, folder_id):
    for key_hash in iter(key_q.get, None):
        store_it.logger.info("Working on {0}".format(key_hash))
        with open("{0}.key".format(key_hash), 'r') as pk_fp, \
                open("{0}.pub".format(key_hash), 'r') as pub_fp:
            store_it.create_file(fname="{0}.key".format(key_hash),
                                 folder_id=folder_id,
                                 body=pk_fp.read())

            store_it.create_file(fname="{0}.pub".format(key_hash),
                                 folder_id=folder_id,
                                 body=pub_fp.read())
            sleep(0.5)
        remove("{0}.key".format(key_hash))
        remove("{0}.pub".format(key_hash))
        key_q.task_done()
    key_q.task_done()


# def write_keys_to_cloud(self, key_hash, private_key, public_key):


if __name__ == '__main__':
    writers = []
    pushers = []
    key_count.value = 0
    store_it = StoreIt()
    folder_id = store_it.get_folder_id(config['folder_name'])

    kpg = KeyPairGenerator(target=config['storage'])
    for _ in range(config['write_workers']):
        writer_p = multiprocessing.Process(target=write_em,
                                           args=(kpg,
                                                 config['keys_per_worker']))
        writers.append(writer_p)

    for _ in range(config['push_workers']):
        pusher_p = multiprocessing.Process(target=push_em,
                                           args=(store_it, folder_id))
        pushers.append(pusher_p)

    # Push em real good
    [p.start() for p in pushers]

    # Kick the writers off!
    [p.start() for p in writers]

    # Wait for the writers to finish - they'll be done loooong before the
    # pushers
    [p.join() for p in writers]

    [key_q.put(None) for _ in pushers]

    key_q.join()

    [p.join() for p in pushers]

# USe a write queue, one process updates a counter somewhere
# from Queue import Queue
# writeQueue = Queue()
# outFile = open(path,'w')
# while writeQueue.qsize():
#   outFile.write(writeQueue.get())
# outFile.flush()
# outFile.close()

# If you terminate, you must join. -T6000
# p.terminate()