'''
Bu kodumda multithread kullandım ancak multiprocessing de kullanabilirdik multiprocessing özellikle CPU-Bound problemler
için daha avantajlıdır aynı zamanda Global Interprete Lock (GIL) sınırlaması thread'lerde geçerlidir ama process'lerde değil her işlem kendi bellek alanında çalıştığı için bağımsızdır
GIL aynı anda sadece bir threadin çalışmasına izin veriri multicore olsa dahi çünkü ortak memory alanıdna değişiklik yapmak yanlış sonuçlar elde edilemsine sebeb olur process memory alanlar ayrıdır
Ancak process daha maliyetli bir işlemdir özellikle memory noktasında o yğzden I/O ağırlıklı işlemlerde thread CPU ağırlıklı işlemlerde process yaklaşımı tercih edilebilir
'''
#Ayni anda birden fazla ithread calistirmak icin projeye import threading modülünü ile ekliyoruz
import threading 
#rastgele uyuma suresini belirlemek icin
import time 
import random

'''
Fork classı tanımlanarak fork nesnelerinin her birini kilitlenebilen
nesne özelliği verilir
'''

class Fork:
    def __init__(
        self,
        index: int,
    ):
        self.index = index
        self.lock = threading.Lock() #her çatal bir lock ile temsil edilir
        #picked_up ve owner izleme ve loglama işlemleri içindir
        self.picked_up = False #çatalın alınıp alınmadığının bilgisidir
        self.owner = -1 #çatalı tutan filozofun ID'si

    def __enter__(self):
        return self

    def __call__(self, owner: int):
        if self.lock.acquire():#lock almayı dener yani kaynağı kendine alır
            self.owner = owner
            self.picked_up = True
            print(self)
        return self
    #Bu metoda çatal bırakılır durumu sona erer
    def __exit__(self, e_t, e_v, e_tb):
        self.lock.release() #çatal bırakılır
        self.picked_up = False
        self.owner = -1
    #kaç numaralı çatalın hangi filozofun elinde olduğu bilgisini basar
    def __str__(self):
        return f"F{self.index:2d} {self.owner:2d}"

# class Philosopher(threading.Thread): threading.Thread bu yapıyla her filozof bir thread olur ve eş zamanlı çalışabilirler
class Philosopher(threading.Thread):
    def __init__(
        self,
        index: int,
        left_fork: Fork,
        right_fork: Fork,
        spaghetti: int,
    ):
        super().__init__(name=f"Philosopher {index:2d}")
        self.index = index               # Filozof numarası
        self.left_fork = left_fork       # Solundaki çatal
        self.right_fork = right_fork     # Sağındaki çatal
        self.spaghetti = spaghetti       # Kaç kez yemek yiyecek?
        self.eating = False              # Şu anda yemek yiyor mu?
    #Filozofun yaşam döngüsü düşün - ye - düşün
    def run(self):
    while self.spaghetti > 0:           # Hâlâ yemek kalmışsa
        self.think()                    # Önce düşün
        self.eat_w_oddeven()           # Sonra yemek ye


    @staticmethod
    def think():
        time.sleep(3 + random.random() * 3) # 3-6 saniye arası düşünme süresi
#eat metodu ile önce sol sonra sağ çatalı alması üzerine kurgulanmış 
#Ancak bu durum Deadlock riski taşır.Bu yüzden eat_w_oddeven() kullanıldı
    def eat(self):
        with self.left_fork(self.index):
            time.sleep(5 + random.random() * 5)
            with self.right_fork(self.index):
                self.spaghetti -= 1
                self.eating = True
                print(self)
                time.sleep(5 + random.random() * 5)
                self.eating = False
'''çift numaralı filozoflar önce sol sonra sağ çatal alır 
tek numaralı filozoflar önce sağ sonra sol çatal 
Bu sayede herkes aynı sırayla çatal almaz deadlock öönlenir
problemin çözümü için kritik nokta burdadır 
İlk önce tekler veya çiftler başlasın dersek önce tekler çatal almaya başlasın sonra çiftler 
bu senaryoda daha z yarış olur ama deadlock riski düşük olduğu için gerekli değil ve 
bazen güncel hayat problemleri bu yaklaşımı kabul etmyebilir bu durumda rastgele tek çift farketmeksizin adaletli bir süreç içinde deadlock önleyen 
algoritmayı oluşturmamızı bekler

'''
    def eat_w_oddeven(self):
        if self.index % 2 == 0:             #çift filozoflar önce sol sonra soğ çatalı alır
            first_fork = self.left_fork
            second_fork = self.right_fork
        else:
            first_fork = self.right_fork     #tek filozoflar önce sağ sonra sol çatalı alırlar
            second_fork = self.left_fork
        #B u asimetrik yaklaşım sayesinde hepsi aynı anda çatala saldırsa bilr çapraz kilitlenmelei engelenmiş olur çünkü herkes aynı sorada çatları almak istememz deadlock riski fazlasıyla düşer
        with first_fork(self.index):
            time.sleep(5 + random.random() * 5)
            with second_fork(self.index):
                self.spaghetti -= 1
                self.eating = True
                print(self)
                time.sleep(5 + random.random() * 5)
                self.eating = False
#Rastgele süreyle yer ve yediğinde spaghetti sayısı azalır program spaghetti halla olduğu sürece çalışır
    def __str__(self):
        return f"P{self.index:2d} {self.spaghetti:2d}"


if __name__ == "__main__":
    n: int = 5 #masadaki filozof sayısı
    m: int = 7  #her bir filozfon yiyeceği yemek sayisi
    forks = [Fork(i) for i in range(n)]#n adet çatal oluşturulur yuvarlak masa biri sağındaki filozofla ortak
    #her filozof solundaki ve sağındaki çatalı alabilir 
    #örneğin n = 5 için ilk 2 ve 4 yiyebilir
    philosophers = [Philosopher(i, forks[i], forks[(i + 1) % n], m) for i in range(n)]
    for philosopher in philosophers:
        philosopher.start() # Tüm filozoflar başlar
    for philosopher in philosophers:
        philosopher.join()  # Tüm filozoflar bitene kadar beklenir
