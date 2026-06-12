import threading
import time

NUM = 5
forks = [threading.Semaphore(1) for _ in range(NUM)]
room_once = threading.Semaphore(1)  # 한번에 요구하기 에서 쓰는 락 룸에대한



# 1) 한번에 요구하기 - 점유대기를 차단하자
# ==========================================


def philosopher_all(id):
    while True:

        room_once.acquire()  # 걍 두 포크를 잡는걸 atomic하게 동작핟로고
        forks[id].acquire()
        forks[(id + 1) % NUM].acquire()
        room_once.release()

        print(f"[한번에 요구하기법] 철학자 {id} 식사 중")
        time.sleep(0.1)

        forks[id].release()
        forks[(id + 1) % NUM].release()


        break



# 2) 자원에 순서 할당해서 주기
# ==========================================

def philosopher_order(id):
    while True:

        # 0~3번 철학자는 왼쪽 포크//  4번 철학자는 오른쪽 포크부터

        first = id if id < 4 else (id + 1) % NUM

        second = (id + 1) % NUM if id < 4 else id

        forks[first].acquire()
        forks[second].acquire()

        print(f"[순서대로 먹기법] 철학자 {id} 식사 중")
        time.sleep(0.1)

        forks[second].release()
        forks[first].release()



        break



# 3) Banker's Algorithm
# ==========================================

# 포크 5갠데 이걸 중앙에서 할당 검사 -> 미리 예측해서 회피해야됨

banker_lock = threading.Condition()
available_forks = NUM


def philosopher_bankers(id):

    global available_forks
    while True:
        with banker_lock:

            # safe state 를 여기서 검사할건데
            # 지금 본인이 2개를 집엇을 떄 다른 사람이 하나만 들게 되는 사람이 있는지 두개 들수있는애가 있나

            while available_forks < 2:

                banker_lock.wait()

            # 안전상태 확인 -> 포크 줌
            available_forks -= 2

            print(f"[Banker's 알고리즘] 철학자 {id} 식사 중 (남은 포크: {available_forks})")

        time.sleep(0.1)

        with banker_lock:

            # 끝나고 자원 반환
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