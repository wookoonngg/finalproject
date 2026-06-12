# === 여기는 세마포어로 생산 소비 문제 ===
import threading
import time
import random

from numpy.f2py.crackfortran import appenddecl

# 버퍼 max 30
MAX = 30
buffer = []

# 세마포어 변수 1 초기화 / empty가 맥스 / fulll 이 없는거
mutex = threading.Semaphore(1)
empty = threading.Semaphore(MAX)
full = threading.Semaphore(0)



# 생산자 함수
# 버퍼가 max면 gotosleep
# 아니면 락 잡고 append
# 완료하면 full에 있는 소비자 깨우기

def producer(id):
    for i in range(50):
        empty.acquire()  # 버퍼 빈공간일 때까지 기다림
        mutex.acquire()  # 뮤텍스 버퍼 권한 얻고

        # 여기가 critical section

        item = f"데이터-{id}-{i}"
        buffer.append(item)
        print(f"[생산자 {id}] '{item}' 생산 | 현재 버퍼 크기: {len(buffer)} / {MAX}")


        mutex.release()  # 버퍼 접근 권한 반환
        full.release()  # 채워진 데이터 개수 증가 (소비자 깨움)

        time.sleep(random.uniform(0.01, 0.05))


def consumer(id):
    for i in range(50):
        full.acquire()  # 채워진 데이터가 있을 때까지 기다리기
        mutex.acquire()  # 버퍼에 대한 독점적 접근 권한 획득

        # 임계 구역 (Critical Section)
        item = buffer.pop(0)
        print(f"[소비자 {id}] '{item}' 소비 | 현재 버퍼 크기: {len(buffer)} / {MAX}")

        mutex.release()  # 버퍼 접근 권한 반환
        empty.release()  # 빈 공간 개수 증가 (생산자 깨움)
        time.sleep(random.uniform(0.01, 0.05))


# 대충 테스트 코드만
# 생산자 0,1  소비자 0,1 둘씩

if __name__ == "__main__":
    threads = []

    for i in range(2):
        threads.append(threading.Thread(target=producer, args=(i,)))
        threads.append(threading.Thread(target=consumer, args=(i,)))

    for t in threads:
        t.start()

    # 조인문으로 같이

    for t in threads:
        t.join()


    print("Producer-Consumer 끝")