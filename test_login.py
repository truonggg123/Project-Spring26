import database

def run_test():
    print("--- CHƯƠNG TRÌNH TEST HỆ THỐNG XÁC THỰC (CONSOLE) ---")
    
    # BƯỚC 1: ĐĂNG KÝ
    print("\n1. Test Đăng ký:")
    user = input("Nhập username mới: ")
    pwd = input("Nhập password: ")
    reg_res = database.register_user(user, pwd)
    print(f"Kết quả: {reg_res['message']}")

    # BƯỚC 2: ĐĂNG NHẬP
    print("\n2. Test Đăng nhập:")
    l_user = input("Nhập username để đăng nhập: ")
    l_pwd = input("Nhập password: ")
    log_res = database.login_user(l_user, l_pwd)
    
    if log_res['success']:
        print(f"✅ ĐĂNG NHẬP THÀNH CÔNG!")
        print(f"Thông tin: ID={log_res['user_id']}, Username='{log_res['username']}'")
    else:
        print(f"❌ ĐĂNG NHẬP THẤT BẠI: {log_res['message']}")

if __name__ == "__main__":
    run_test()