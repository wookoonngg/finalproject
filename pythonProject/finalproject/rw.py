import threading
import time
import random

# 공통 자원
read_count = 0
write_count = 0
resource_data = "초기 데이터"

# 세마포어
resource_mutex = threading.Semaphore(1)  # 실제 자원에 대한 접근 제어
rmutex = threading.Semaphore(1)  # read_count 보호용
wmutex = threading.Semaphore(1)  # write_count 보호용
read_try = threading.Semaphore(1)  # Writer Preference에서 Reader 진입 차단용


# ==========================================
# 1) Reader Preference (독자 우선 방식)
# ==========================================
def reader_rp(id):
    global read_count
    time.sleep(random.uniform(0.01, 0.05))  # 스레드 섞임을 위한 대기

    rmutex.acquire()
    read_count += 1
    if read_count == 1:  # 첫 번째 독자일 경우
        resource_mutex.acquire()  # 작성자 접근 차단
    rmutex.release()

    # 임계 구역 (읽기)
    print(f"[독자 우선 - 독자 {id}] 읽기 완료: {resource_data}")
    time.sleep(0.1)

    rmutex.acquire()
    read_count -= 1
    if read_count == 0:  # 마지막 독자일 경우
        resource_mutex.release()  # 작성자 접근 허용
    rmutex.release()


def writer_rp(id):
    global resource_data
    time.sleep(random.uniform(0.01, 0.05))

    resource_mutex.acquire()
    # 임계 구역 (쓰기)
    resource_data = f"작성자 {id}가 수정한 데이터"
    print(f"[독자 우선 - 작성자 {id}] 쓰기 완료")
    time.sleep(0.1)
    resource_mutex.release()


# ==========================================
# 2) Writer Preference (작성자 우선 방식)
# ==========================================
def reader_wp(id):
    global read_count
    time.sleep(random.uniform(0.01, 0.05))

    read_try.acquire()  # 작성자가 대기 중이면 여기서 차단됨
    rmutex.acquire()
    read_count += 1
    if read_count == 1:
        resource_mutex.acquire()
    rmutex.release()
    read_try.release()

    # 임계 구역 (읽기)
    print(f"[작성자 우선 - 독자 {id}] 읽기 완료: {resource_data}")
    time.sleep(0.1)

    rmutex.acquire()
    read_count -= 1
    if read_count == 0:
        resource_mutex.release()
    rmutex.release()


def writer_wp(id):
    global write_count, resource_data
    time.sleep(random.uniform(0.01, 0.05))

    wmutex.acquire()
    write_count += 1
    if write_count == 1:  # 첫 번째 작성자가 진입 의사를 밝히면
        read_try.acquire()  # 새로운 독자의 진입을 차단
    wmutex.release()

    resource_mutex.acquire()
    # 임계 구역 (쓰기)
    resource_data = f"작성자 {id}가 수정한 데이터"
    print(f"[작성자 우선 - 작성자 {id}] 쓰기 완료")
    time.sleep(0.1)
    resource_mutex.release()

    wmutex.acquire()
    write_count -= 1
    if write_count == 0:  # 모든 작성자가 작업을 마치면
        read_try.release()  # 독자의 진입을 다시 허용
    wmutex.release()


# ==========================================
# 실행 테스트 파트 (이전에 누락되었던 부분)
# ==========================================
if __name__ == "__main__":
    print("=== 1) Reader Preference (독자 우선) 테스트 시작 ===")
    threads_rp = []
    # 3명의 독자와 3명의 작성자 스레드 생성
    for i in range(3):
        threads_rp.append(threading.Thread(target=writer_rp, args=(i,)))
        threads_rp.append(threading.Thread(target=reader_rp, args=(i,)))

    for t in threads_rp: t.start()
    for t in threads_rp: t.join()

    print("\n=== 2) Writer Preference (작성자 우선) 테스트 시작 ===")
    # 초기화
    read_count = 0
    write_count = 0
    resource_data = "초기 데이터"

    threads_wp = []
    # 3명의 독자와 3명의 작성자 스레드 생성
    for i in range(3):
        threads_wp.append(threading.Thread(target=writer_wp, args=(i,)))
        threads_wp.append(threading.Thread(target=reader_wp, args=(i,)))

    for t in threads_wp: t.start()
    for t in threads_wp: t.join()

    print("\nReaders-Writers Problem 작업 완료")