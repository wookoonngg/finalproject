import threading
import time

NUM = 5
forks = [threading.Semaphore(1) for _ in range(NUM)]
room_once = threading.Semaphore(1)  # Method 1용 전역 락


# ==========================================
# Method 1: Requesting all resources (한 번에 요구)
# ==========================================
def philosopher_all(id):
    while True:
        room_once.acquire()  # 두 포크를 집는 행위 자체를 원자적(Atomic)으로 만듦
        forks[id].acquire()
        forks[(id + 1) % NUM].acquire()
        room_once.release()

        print(f"[Method 1] 철학자 {id} 식사 중")
        time.sleep(0.1)

        forks[id].release()
        forks[(id + 1) % NUM].release()
        break


# ==========================================
# Method 2: Resource Ordering (자원 순서 할당)
# ==========================================
def philosopher_order(id):
    while True:
        # 0~3번 철학자는 왼쪽(id) 포크부터, 4번 철학자는 오른쪽((id+1)%5) 포크부터 집음
        first = id if id < 4 else (id + 1) % NUM
        second = (id + 1) % NUM if id < 4 else id

        forks[first].acquire()
        forks[second].acquire()

        print(f"[Method 2] 철학자 {id} 식사 중")
        time.sleep(0.1)

        forks[second].release()
        forks[first].release()
        break


# ==========================================
# Method 3: Banker's Algorithm (회피, 가산점)
# ==========================================
# 5개의 포크(가용 자원)를 중앙에서 할당 검사
banker_lock = threading.Condition()
available_forks = NUM


def philosopher_bankers(id):
    global available_forks
    while True:
        with banker_lock:
            # 안전 상태(Safe State) 검사:
            # 내가 2개를 집었을 때 남은 사람이 식사할 수 있는지(남은 포크가 1개 이상인지)
            # 식사하려면 최소한 포크 2개가 한 번에 필요함 (단순화된 은행원 알고리즘)
            while available_forks < 2:
                banker_lock.wait()

            # 자원 할당 (안전 상태이므로 포크 2개를 한 번에 가져감)
            available_forks -= 2
            print(f"[Banker's] 철학자 {id} 식사 중 (남은 포크: {available_forks})")

        time.sleep(0.1)

        with banker_lock:
            # 자원 반환
            available_forks += 2
            banker_lock.notify_all()
        break


# 테스트 실행부
if __name__ == "__main__":
    for target_method in [philosopher_all, philosopher_order, philosopher_bankers]:
        threads = [threading.Thread(target=target_method, args=(i,)) for i in range(NUM)]
        for t in threads: t.start()
        for t in threads: t.join()
        print("-" * 30)