import threading
import random
import numpy as np
'''
Bu koda amac Monte Carlo Yöntemini kullanarak π (pi) sayısını tahmin eden
multithread bir python programıdır
hesaplamaları hızlandırmak için birden fazla thread kullanılır
Ancak GIL'in etkilediği bir versiyondur yani python yorumlayıcısındaki kilit nedeniyle gerçek anlamda paralel çalışmaz
Python yorumlayıcısı aynı anda sadece 1 thread'in bytecode çalıştırmasına izin verir.
'''
#Bu sınıf threading.Thread'den kalıtım alır 
#her bir thread kendi rastgle noktalarını üretip hesaplama yapar 


class PiEstimatorThread(threading.Thread):
    def __init__(
        self,
        number_of_points: int = 100000,     #bir threadin kaç nokta oluşturacağını belirler
        name="Generator",                   #threade isim verilir
    ):
        super().__init__(name=name)
        self.number_of_points = number_of_points
        self.inner_points = 0
        self.total_points = 0
#Bu method self.number_of_points kadar nokta üretir ve her birinin çember içinde olup olmadığını kontrol eder.
#nokta çember içinde ise sayaç artırılır
    def generate_points(self):
        for _ in range(self.number_of_points):   
            x = random.random()
            y = random.random()
            if x**2 + y**2 <= 1:
                self.inner_points += 1
            self.total_points += 1
#thread çalıştırıldığında yapılacak işlem thread.start() çağrıldığında otomotik olarak çalışır
    def run(self):
        self.generate_points()

#Bu sınıf ise tüm iş parçacıklarını yönetir ve pi'yi hesaplar
#threading.Thread'den üretilmiştir Aslında ana yönetici iş parçacığıdır
class PiEstimator(threading.Thread):
    def __init__(
        self,
        desired_accuracy: float = 1.0e-4,
        number_of_threads: int = 4,
        chunk_size: int = 100000,
        name="PI Estimator",
    ):
        super().__init__(name=name)
        self.desired_accuracy = desired_accuracy    #Pi'nin gerçek değerine ne kadar yakın olunması istendiği.
        self.number_of_threads = number_of_threads  #Her döngüde kaç thread kullanılacağı
        self.chunk_size = chunk_size                #Her thread'in kaç nokta üreteceği.
        self.inner_points = 0       
        self.total_points = 0       
        self.generated_threads = 0                  #Toplam kaç thread üretildi, sayaç.
#pi değerini hesaplayan ve hata analizini yapan fonksiyon
    def pi(self):
        try:
            return 4 * self.inner_points / self.total_points
        except ZeroDivisionError:
            return 0.0
#Monte Carlo formülüyle π tahmin edilir.
    def accuracy(self):
        return abs(np.pi - self.pi())

    def run(self):
        while self.accuracy() > self.desired_accuracy: # Doğruluk seviyesi istenen seviyeye ulaşana kadar döngü devam eder.
            threads = []
            #yeni threadler oluşturulur
            for _ in range(self.number_of_threads):
                threads.append(
                    PiEstimatorThread(
                        number_of_points=self.chunk_size,
                        name=f"Generator - {self.generated_threads}",
                    )
                )
                self.generated_threads += 1
                #threadler başlatılır
            for thread in threads:
                thread.start()
                #join ile her threadin işi bitene kadar bekletilir
            for thread in threads:
                thread.join()

                #threadlerin ürettiği sonuçlar toplanılır
            for thread in threads:
                self.inner_points += thread.inner_points
                self.total_points += thread.total_points
#Sonuçlar yazdırılır
'''
    join() burada override edilmiştir çünkü thread bittiğinde:
    Kaç nokta üretildi?
    Kaç tanesi çemberin içindeydi?
    Son π tahmini ne?
    Hata payı ne?
    bunları yazmak istiyoruz. Bu yüzden super().join() ile normal bekleme yapılır, sonra da çıktılar yazdırılır.
'''
    def join(self, timeout=None):
        super().join()
        print(f"Final estimation of Pi: {self.pi()}")
        print(f"Accuracy: {self.accuracy()}")
        print(f"Number of total points: {self.total_points}")
        print(f"Number of inner points: {self.inner_points}")
        print(f"Number of threads: {self.generated_threads}")


if __name__ == "__main__":
    pi_estimator = PiEstimator(
        desired_accuracy=1.0e-7,
        number_of_threads=8,
        chunk_size=10000000,
        name="Pi Estimator",
    )
    pi_estimator.start()
    pi_estimator.join()
