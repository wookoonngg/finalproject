import threading
import time
import random

MAX = 30  # 버퍼의 최대 크기 설정
buffer = []

# 동기화를 위한 세마포어 초기화
mutex = threading.Semaphore(1)  # 임계 구역 접근 제어 (상호 배제)
empty = threading.Semaphore(MAX)  # 버퍼 내 빈 공간의 개수 (초기값 30)
full = threading.Semaphore(0)  # 버퍼 내 채워진 데이터의 개수 (초기값 0)


def producer(id):
    for i in range(50):
        empty.acquire()  # 빈 공간이 있을 때까지 대기
        mutex.acquire()  # 버퍼에 대한 독점적 접근 권한 획득

        # 임계 구역 (Critical Section)
        item = f"데이터-{id}-{i}"
        buffer.append(item)
        print(f"[생산자 {id}] '{item}' 생산 | 현재 버퍼 크기: {len(buffer)} / {MAX}")

        mutex.release()  # 버퍼 접근 권한 반환
        full.release()  # 채워진 데이터 개수 증가 (소비자 깨움)
        time.sleep(random.uniform(0.01, 0.05))


def consumer(id):
    for i in range(50):
        full.acquire()  # 채워진 데이터가 있을 때까지 대기
        mutex.acquire()  # 버퍼에 대한 독점적 접근 권한 획득

        # 임계 구역 (Critical Section)
        item = buffer.pop(0)
        print(f"[소비자 {id}] '{item}' 소비 | 현재 버퍼 크기: {len(buffer)} / {MAX}")

        mutex.release()  # 버퍼 접근 권한 반환
        empty.release()  # 빈 공간 개수 증가 (생산자 깨움)
        time.sleep(random.uniform(0.01, 0.05))


# 테스트 실행
if __name__ == "__main__":
    threads = []
    # 2명의 생산자와 2명의 소비자 스레드 생성
    for i in range(2):
        threads.append(threading.Thread(target=producer, args=(i,)))
        threads.append(threading.Thread(target=consumer, args=(i,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Producer-Consumer 작업 완료")