from flask import Flask, render_template, request, redirect, url_for
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time # デバッグのために一時停止するために使用

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
app = Flask(__name__)

def get_panda_site_json(username, password):
    """
    京都大学のPandAにログインし、https://panda.ecs.kyoto-u.ac.jp/direct/assignment/my.json から情報を取得します。

    Args:
        username (str): 京都大学のユーザーID (学生番号など)。
        password (str): 統合認証パスワード。

    Returns:
        dict: assignment/my.jsonから取得したデータ。取得に失敗した場合はNone。
    """
    LOGIN_URL = "https://panda.ecs.kyoto-u.ac.jp/cas/login?service=https%3A%2F%2Fpanda.ecs.kyoto-u.ac.jp%2Fsakai-login-tool%2Fcontainer"
    TARGET_JSON_URL = "https://panda.ecs.kyoto-u.ac.jp/direct/assignment/my.json"

    
    try:
        # WebDriverの初期化 (Chromeを使用)
        # chromedriverがPATHにあるか、スクリプトと同じディレクトリにあることを想定
        
        # ヘッドレスモードで実行する場合 (ブラウザウィンドウを表示しない)
        # options.add_argument("--headless")
        # options.add_argument("--disable-gpu") # Windowsの場合、headlessで必要になることがある
        # options.add_argument("--no-sandbox") # Dockerなど一部環境で必要になることがある
        
        
        driver.get(LOGIN_URL)
        

        # 1. ログイン処理
        
        username_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.NAME, "submit"))
        )
        login_button.click()
        

        # ログイン成功の確認 (URLの変更を待つ)
        # ログイン成功後、/portal または /sakai-login にリダイレクトされることを期待
        try:
            WebDriverWait(driver, 20).until(
                EC.url_contains("https://panda.ecs.kyoto-u.ac.jp/portal") or
                EC.url_contains("https://panda.ecs.kyoto-u.ac.jp/sakai-login") # ログイン処理中に一時的にこのURLになることがある
            )
            print(f"ログイン後のURL: {driver.current_url}")
            if "login" in driver.current_url:
                print("ログインに失敗した可能性があります。ユーザー名またはパスワードを確認してください。")
                return 401
            print("ログインに成功しました。")

        except TimeoutException:
            print("ログイン後のリダイレクトが時間内に完了しませんでした。")
            print(f"現在のURL: {driver.current_url}")
            try:
                error_message_element = driver.find_element(By.ID, "msg")
                print(f"CASエラーメッセージ: {error_message_element.text}")
            except NoSuchElementException:
                pass
            return None

        # 2. ログイン後のセッションでターゲットのJSON URLにアクセス
        
        driver.get(TARGET_JSON_URL)

        # ページのソースコードを取得（JSONデータがそのまま表示されていることを期待）
        page_source = driver.page_source

        # WebDriverで直接JSONをパースする機能はないため、ソースを文字列として取得し、JSONとして解析
        # ただし、JSONデータがHTMLタグに囲まれている場合は、その部分を抽出する必要がある
        # このURLの場合、直接JSONが返されると想定
        
        # 'pre' タグなどに囲まれている可能性があるため、その場合は抽出する
        # 例: <pre style="word-wrap: break-word; white-space: pre-wrap;">{...json...}</pre>
        try:
            pre_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))
            )
            json_text = pre_element.text
        except TimeoutException:
            # preタグがない場合は、bodyのテキストを直接取得を試みる
            # print("preタグが見つかりませんでした。bodyのテキストを直接解析を試みます。")
            json_text = driver.find_element(By.TAG_NAME, "body").text
            
        # JSON文字列をPythonの辞書に変換
        try:
            data = json.loads(json_text)
            # print("JSONデータを正常に取得し、解析しました。")
            return data
        except json.JSONDecodeError as e:
            print(f"JSONデータの解析に失敗しました: {e}")
            print("取得したテキストの一部:")
            print(json_text[:500]) # エラー時のデバッグ用
            return None

    except TimeoutException:
        print("タイムアウトエラー: ページの要素が見つかるか、操作が完了するまでに時間がかかりすぎました。")
        return 404
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        return 999
    
    
def get_course_name(id):
    driver.get(id)
    json_data=driver.find_element(By.TAG_NAME, "body").text
    data = json.loads(json_data)
    return data

def quit_brouse():
    if driver:
            print("ブラウザを閉じます。")
            driver.quit()
    

#
    # !!!重要!!! 以下のプレースホルダーを実際の情報に置き換えてください。

    print("--- PandA JSONデータ取得開始 ---")
    

    

#ホームページ
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logined')
def login():
    out_data=""
    username=request.form('username')
    password=request.form('password')
    json_data = get_panda_site_json(username,password)
    data=json_data["assignment_collection"]
    l=len(data)
    assig=[]
    print("未提出の課題一覧")
    for i in range (0,l):
        if (data[i]["status"]=="OPEN") and ((data[i]["submissions"]== None) or (data[i]["submissions"][0]["userSubmission"]== False)):
            sid=str(data[i]["context"])
            site="https://panda.ecs.kyoto-u.ac.jp/direct/site/"+sid+".json"
            namej=get_course_name(site)
            name=namej["title"]
            course_name=("コース名："+name)
            assig_name=("課題名："+data[i]["title"])
            tl=int(data[i]["dueTime"]["epochSecond"])
            rem=tl-time.time()
            da=int(rem//86400)
            ho=int((rem-da*86400)//3600)
            mi=int((rem-da*86400-ho*3600)//60)
            se=int(rem % 60)
            due_data=("提出期限まで：残り"+str(da)+"日"+str(ho)+"時間"+str(mi)+"分"+str(se)+"秒")
            out_data=out_data+"\n<h2>"+course_name+"</h2>"+"\n<h3>"+assig_name+"</h3>"+"\n<h3>"+due_data+"</h3>"
