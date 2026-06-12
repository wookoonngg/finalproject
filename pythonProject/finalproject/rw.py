import threading
import time
import random

# 공통 자원
read_count = 0
write_count = 0
resource_data = "초기 데이터"

# 세마포어
resource_mutex = threading.Semaphore(1)  # 그 디비에 대한 뮤텍스
rmutex = threading.Semaphore(1)  # read카운트 가드
wmutex = threading.Semaphore(1)  # 작자 보호 가드
read_try = threading.Semaphore(1)  # 작가 우선에서 리더 막기



# 1. 독자우선 방식
# ---------------


def reader_rp(id):
    global read_count
    time.sleep(random.uniform(0.01, 0.05))  # 스레드 섞일 수 있어서 대기

    rmutex.acquire()
    # 리더 변수 락 잡고

    read_count += 1
    #  리더 카운트 +1

    if read_count == 1:  # 첫 번째 독자면
        resource_mutex.acquire()  # 내가 락잡고

    rmutex.release()

    # critical section 읽기
    print(f"[독자 우선 - 독자 {id}] 읽기 완료: {resource_data}")
    time.sleep(0.1)

    #  다시 리더 카운트락잡고 -- 해야됨
    rmutex.acquire()
    read_count -= 1

    if read_count == 0:  # 마지막 독자면
        resource_mutex.release()  # db 락 풀어


    rmutex.release()

#  작성자는 걍 락 허가 떨어지면 쓰면도됨

def writer_rp(id):
    global resource_data

    time.sleep(random.uniform(0.01, 0.05))

    resource_mutex.acquire()
    # 임계 구역 (쓰기)

    resource_data = f"작성자 {id}가 수정한 데이터"
    print(f"[독자 우선 - 작성자 {id}] 쓰기 완료")
    time.sleep(0.1)

    resource_mutex.release()



# 2. 작성자 우선 방식
# ==================


def reader_wp(id):
    global read_count
    time.sleep(random.uniform(0.01, 0.05))

    read_try.acquire()  # 작성자가 있으면 걍 여기서 블락

    # rmutex.acquire()
    # read_count += 1
    # if read_count == 1:
    #     resource_mutex.acquire()
    #
    # rmutex.release()
    #  작성자우선이라 이건 필요없을 듯

    read_try.release()

    # critical section
    print(f"[작성자 우선 - 독자 {id}] 읽기 완료: {resource_data}")
    time.sleep(0.1)


    # rmutex.acquire()
    # read_count -= 1
    # if read_count == 0:
    #     resource_mutex.release()
    # rmutex.release()


def writer_wp(id):

    global write_count, resource_data
    time.sleep(random.uniform(0.01, 0.05))

    # 작성자 락잡고 숫자 올리기
    wmutex.acquire()
    write_count += 1

    if write_count == 1:  # 첫 번째 작성자 들어오면

        read_try.acquire()  # 락잡고
    wmutex.release()

    resource_mutex.acquire()

    # critical area
    resource_data = f"작성자 {id}가 수정한 데이터"
    print(f"[작성자 우선 - 작성자 {id}] 쓰기 완료")
    time.sleep(0.1)

    resource_mutex.release()

    wmutex.acquire()
    write_count -= 1

    if write_count == 0:  # 모든 작성자가 작업을 마치면
        read_try.release()  # 독자의 진입을 다시 허용

    wmutex.release()



# 테스트 코드
# ===============
if __name__ == "__main__":
    print("=== 1) Reader Preference (독자 우선) ===")
    threads_rp = []


    # 둘다 셋셋 012
    for i in range(3):
        threads_rp.append(threading.Thread(target=writer_rp, args=(i,)))
        threads_rp.append(threading.Thread(target=reader_rp, args=(i,)))

    for t in threads_rp: t.start()
    for t in threads_rp: t.join()

    print("\n=== 2) Writer Preference (작성자 우선) ===")


    # 초기화
    read_count = 0
    write_count = 0
    resource_data = "초기 데이터"

    threads_wp = []


    # 3,3독자 작자 스레드

    for i in range(3):
        threads_wp.append(threading.Thread(target=writer_wp, args=(i,)))
        threads_wp.append(threading.Thread(target=reader_wp, args=(i,)))

    for t in threads_wp: t.start()
    for t in threads_wp: t.join()

    print("\nReaders-Writers Problem 끝")