import random
import math
import multiprocessing
from task_katan import checks


POOL = multiprocessing.get_context('fork').Pool(processes=10)
ROUNDS = 84
WEIGHT = 31
CIPHER_NAME = "KATAN32"


def verify(in_diff, out_diff, rounds, boomerang, offset=0):
    test_n = 2**WEIGHT
    key = random.randint(0, 2**32)
    records = set()
    count = 0
    result = 0
    task_list = []
    while count < test_n:
        x1 = random.randint(0, 2**32)
        if x1 in records:
            continue
        if x1 > (x1 ^ in_diff):
            continue
        count += 1
        records.add(x1)
    records = list(records)
    batch_size = 100000
    batch_num = int(len(records) / batch_size)
    for i in range(0, batch_num):
        task_list.append(
            POOL.apply_async(
                checks,
                args=(
                    records[i * batch_size : i * batch_size + batch_size],
                    key,
                    in_diff,
                    out_diff,
                    rounds,
                    offset,
                    boomerang
                ),
            )
        )
    for task in task_list:
        result += task.get()
    if result == 0:
        return "Invalid"
    prob = result / (batch_size* batch_num)
    return str(math.log2(prob))


if __name__ == "__main__":
    result_file_name = 'verify_result_katan32-{0}.txt'.format(ROUNDS+1)

    save_file = open(result_file_name, "w")
    data_file = open("check_list_katan32.txt", "r")
    data_list = []
    data = data_file.readline()
    while data != "":
        temps = data.split(",")
        data = []
        for i in temps:
            if i.startswith("0x"):
                data.append(int(i, 16))
            else:
                data.append(int(i))
        data.append(1)
        data_list.append(data)
        data = data_file.readline()


    for dd in data_list:
        res = verify(dd[0], dd[3], ROUNDS, True)
        save_str = "CIPHER:{0}, INPUT_DIFF:{1}, OUTPUT_DIFF:{2}\n\t PROB:{3}\n".format(CIPHER_NAME, dd[0], dd[3], res)



