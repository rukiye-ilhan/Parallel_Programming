'''
Barrier Condition Deadlock Semaphore Lock/Counter 
kavramlarını threadlerde ne amaçla ve nasıl  kullanıldığın kodlarla anlatıcam.
Öncellikle bbu konuların ortak amacı, çok iş parçacıklı (multi-threaded) programlamada eşzamanlılık (concurrency) problemlerini doğru yönetmektir.
Birden fazla thread aynı anda çalışırken, veri tutarlılığını sağlamak, senkronizasyonu yönetmek ve kilitlenme gibi hataları önlemek.
'''
#BARRIER
'''
Amaç: Belirli sayıda iş parçacığı (thread) aynı noktaya gelene kadar bekletilir. Hepsi o noktaya gelince birlikte devam ederler.
Neden Kullanılır: Eş zamanlı işlemlerin senkronize başlamasını sağlamak.
Öreneğin feribotun kapısını yakalamk için birbirleriyle yarştıracağımız 
araçların adil bir şekilde yarışması için lock'larla kontrol edilen gişelerden geçip ortak bir alanda barrier engeliyle toplanmalarını sağlarız
'''
import threading
import time
import random

barrier = threading.Barrier(3)  # 3 thread bariyere gelene kadar bekleyecek
def worker(thread_id):
    print(f"T-{thread_id}: Reached the barrier.")  # Bariyere geldiğini bildir
    time.sleep(3 + random.random() * 10)            # Rastgele süre bekle
    print(f"T-{thread_id} is ready")                # Hazır olduğunu bildir
    barrier.wait()                                  # Bariyer noktasında bekle
    print(f"T-{thread_id}: Passed the barrier!")    # Üçü de gelince devam eder
threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]

for t in threads:
    t.start()

for t in threads:
    t.join()

#CONDITION
'''
Amaç: Üretici-tüketici gibi senaryolarda, bir thread başka bir thread’in belirli bir durumu gerçekleştirmesini bekler.
Neden Kullanılır: Duruma bağlı eş zamanlama yapılmasını sağlar.
'''
import threading
import time

condition = threading.Condition()
shared_data = []


def producer():
    with condition:                                 # Lock edinilir
        print("Producer: Adding item to shared_data.")
        time.sleep(1)
        shared_data.append("data")                  # Veri eklenir
        condition.notify()                          # Tüketiciye haber verilir


def consumer():
    with condition:
        print("Consumer: Waiting for data...")
        condition.wait()                            # Veri gelene kadar bekler
        print(f"Consumer: Got {shared_data.pop()}!")# Veri alındıktan sonra işler


consumer_thread = threading.Thread(target=consumer)
producer_thread = threading.Thread(target=producer)

consumer_thread.start()
producer_thread.start()

consumer_thread.join()
producer_thread.join()

#Deadlock
'''
Amaç: Aynı anda birden fazla thread’in, birbirini beklemesi sonucu programın durmasını gösterir (istenmeyen bir durumdur).
Neden Anlatılır: Hatalı eş zamanlama örneğidir, nasıl oluştuğu ve nasıl engelleneceği öğretilir.
'''


import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()


def thread_func1():
    with lock_a:
        print("Thread 1: Holding lock_a...")
        time.sleep(1)
        with lock_b:
            print("Thread 1: Acquired lock_b!")


def thread_func2():
    with lock_b:
        print("Thread 2: Holding lock_b...")
        time.sleep(1)
        with lock_a:
            print("Thread 2: Acquired lock_a!")


t1 = threading.Thread(target=thread_func1)
t2 = threading.Thread(target=thread_func2)

t1.start()
t2.start()

t1.join()
t2.join()

# Semaphore 
'''
Amaç: Aynı anda sınırlı sayıda thread’in belirli bir bölgeye girmesini sağlar.
Neden Kullanılır: Kaynak sınırlaması olan durumları kontrol etmek için.
'''

import threading
import time

semaphore = threading.Semaphore(2)


def task(thread_id):
    print(f"T-{thread_id}: Waiting for semaphore")
    semaphore.acquire()
    print(f"T-{thread_id}: Acquired semaphore!")
    time.sleep(1)
    semaphore.release()
    print(f"T-{thread_id}: Released semaphore!")


threads = [threading.Thread(target=task, args=(i,)) for i in range(6)]

for t in threads:
    t.start()

for t in threads:
    t.join()

#COUNTER
'''
Amaç: Ortak bir veriye çok sayıda thread erişirken veri tutarlılığını sağlamak.
Neden Kullanılır: Yarış durumu (race condition) oluşmaması için lock kullanılır.
'''
import threading


class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increase(self):
        with self.lock:       # Veri güvenliği için lock
            self.count += 1


class IncreaseCounter(threading.Thread):
    def __init__(self, counter, n):
        super().__init__()
        self.counter = counter
        self.n = n

    def run(self):
        for _ in range(self.n):
            self.counter.increase()


def main(n: int, m: int):
    counter = Counter()
    threads = []
    for _ in range(m):
        t = IncreaseCounter(counter, n)   # Her thread n kez arttıracak
        threads.append(t)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"Expected: {n*m}, Actual: {counter.count}")
    return counter.count


if __name__ == "__main__":
    main(1000000, 4)
