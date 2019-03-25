from multiprocessing import Process, Queue
from time import sleep
from typing import Callable, Iterable


def __worker(work, time_sleep, task_queue, done_queue):
    """

    :param work:
    :type work: Callable[[object], (bool, object)]
    :param time_sleep:
    :type time_sleep: float
    :param task_queue:
    :type task_queue: Queue
    :param done_queue:
    :type done_queue: Queue
    :return:
    """
    for task in iter(task_queue.get, 'STOP'):
        ok, result = work(task)
        done_queue.put((result, task))
        if ok:
            print("OK   {}".format(task))
        else:
            print("FAIL {}".format(task))

        sleep(time_sleep)


def distribute_work(task_generator, func_work, time_sleep, pools=4):
    """

    :param task_generator:
    :type task_generator: Callable[[], (Iterable, int)]
    :param func_work:
    :type func_work: Callable[[object], (bool, object)]
    :param time_sleep:
    :type time_sleep: float
    :param pools:
    :type pools: int
    :return:
    :rtype: Iterable
    """
    # https://docs.python.org/ko/3/library/multiprocessing.html#multiprocessing-examples

    # Distribute pages to crawl
    tasks, total_task = task_generator()

    # Create queues
    queue_task = Queue()
    queue_done = Queue()

    # Submit tasks
    for task in tasks:
        queue_task.put(task)

    # Start worker process
    for _ in range(pools):
        Process(target=__worker, args=(func_work, time_sleep, queue_task, queue_done)).start()

    print("Started!")

    # Collect unordered results
    result_list = []
    success_once = set()
    failed_once = set()
    while len(success_once) + len(failed_once) != total_task or not queue_task.empty():
        try:
            result = queue_done.get()
        except:
            continue

        if result[0]:
            success_once.add(result[1])
            result_list.append(result[0])
        else:
            # Retry once
            if result[1] not in failed_once:
                failed_once.add(result[1])
                queue_task.put(result[1])

    # Stop
    for _ in range(pools):
        queue_task.put('STOP')

    # Print failed ones
    for task_fail in failed_once:
        print("Failed: {}".format(task_fail))

    print("Stopped all!")

    return result_list
