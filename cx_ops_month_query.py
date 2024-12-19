from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import re
import json
import pymysql as pymysql

app = Flask(__name__)


def get_next_month(query_month):
    # 校验格式为 YYYY-MM
    pattern = r"^\d{4}-(0[1-9]|1[0-2])$"
    if not re.match(pattern, query_month):
        return None

    try:
        # 将输入的月份转换为 datetime 对象
        first_day_of_month = datetime.strptime(query_month, "%Y-%m")
        # 计算下一个月份的第一天
        next_month = first_day_of_month + timedelta(days=31)
        # 返回格式化为 YYYY-MM 的下一个月份
        next_month_str = next_month.strftime("%Y-%m")
        return next_month_str
    except ValueError:
        return None


def load_config():
    with open('bladex_jdbc.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        start_date = None
        end_date = None
        next_month = None
        users_cnt = None
        users_add_cnt = None
        all_device_cnt = None
        add_devices_cnt = None
        all_projects_cnt = None
        add_projects_cnt = None
        project_city_cnt = None
        user_mau_cnt = None
        if request.method == 'POST':
            query_month = request.form.get('query_month')
            next_month = get_next_month(query_month)
            if not next_month:
                return jsonify({"error": "输入的月份格式不正确或非法，请重新输入！"}), 500
            start_date = query_month + '-01'
            start_date_time = start_date + ' 00:00:00'
            end_date = next_month + '-01'
            end_date_time = end_date + ' 00:00:00'
            print(f"开始时间：{start_date_time}，结束时间：{end_date_time}")
            # 1.链接mysql
            config = load_config()
            conn = pymysql.connect(host=config['host'], port=config['port'],
                                   user=config['user'],
                                   password=config['password'], charset='utf8', db=config['db'])
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            print("已经连接到数据库！")
            # 2.查询数据
            query_platform_all_users_cnt = "select count(1) as user_cnt from blade_user where is_deleted = 0 and create_time<'" + end_date_time + "'"
            query_platform_add_users_cnt = "select count(1) as user_add_cnt from blade_user where is_deleted = 0 and create_time >= '" + start_date_time + "' and create_time<'" + end_date_time + "'"
            # query_platform_all_devices_cnt = "select sum(a) as all_device_cnt from (select count(1) as a from t_device where is_deleted = 0 and (create_time < '" + end_date_time + "' or create_time is null) union all select count(1)  as a from charging_device_property where is_deleted = 0 and (create_time < '" + end_date_time + "' or create_time is null) union all select count(1)  as a from tgeem_oe_device_new where is_deleted = 0  and (create_time < '" + end_date_time + "' or create_time is null) union all select count(1)  as a from yxfk_hcgr_steam_property where is_deleted = 0  and (create_time < '" + end_date_time + "' or create_time is null) union all select count(1)  as a from yxfk_xcpw_device_property where is_deleted = 0  and (create_time < '" + end_date_time + "' or create_time is null) union all select count(1)  as a from yxfk_ycbsq_electricity_property where is_deleted = 0  and (create_time < '" + end_date_time + "' or create_time is null) ) as temp"
            # query_platform_add_devices_cnt = "select sum(a) as add_devices_cnt from (select count(1) as a from t_device where is_deleted = 0 and ( create_time >= '" + start_date_time + "' and create_time < '" + end_date_time + "') union all select count(1)  as a from charging_device_property where is_deleted = 0 and ( create_time >= '" + start_date_time + "' and create_time < '" + end_date_time + "') union all select count(1)  as a from tgeem_oe_device_new where is_deleted = 0  and (create_time >= '" + start_date_time + "' and create_time < '" + end_date_time + "') union all select count(1)  as a from yxfk_hcgr_steam_property where is_deleted = 0  and ( create_time >= '" + start_date_time + "' and create_time < '" + end_date_time + "') union all select count(1)  as a from yxfk_xcpw_device_property where is_deleted = 0  and ( create_time >= '" + start_date_time + "' and create_time < '" + end_date_time + "') union all select count(1)  as a from yxfk_ycbsq_electricity_property where is_deleted = 0  and ( create_time >= '" + start_date_time + "' and create_time < '" + end_date_time + "') ) as temp"
            query_platform_all_projects_cnt = "select count(1) as all_projects_cnt  from blade_project where is_deleted = 0 and create_time<'" + end_date_time + "'"
            query_platform_add_projects_cnt = "select count(1) as add_projects_cnt from blade_project where is_deleted = 0 and create_time >= '" + start_date_time + "' and create_time<'" + end_date_time + "'"
            # query_platform_project_city_cnt = "select count(distinct v.city) as project_city_cnt from (select DISTINCT city from blade_project where is_deleted = 0 and city is not null AND city!='' UNION select DISTINCT city_name as city from charging_open_city  where is_deleted = 0 and city_name is not null  AND city_name!='') v"
            # query_charge_user_mau_cnt = "select count(DISTINCT create_user ) as user_mau_cnt from charging_order WHERE create_user is not null and start_date>='" + start_date + "' and start_date<'" + end_date + "'  and is_deleted=0"
            cursor.execute(query_platform_all_users_cnt)
            all_users_cnt = cursor.fetchone()
            users_cnt = all_users_cnt['user_cnt']
            print("1️⃣平台总用户数：", users_cnt)

            cursor.execute(query_platform_add_users_cnt)
            users_add_cnt_data = cursor.fetchone()
            users_add_cnt = users_add_cnt_data['user_add_cnt']
            print("2️⃣平台本月新增用户数：", users_add_cnt)

            # cursor.execute(query_platform_all_devices_cnt)
            # all_devices_cnt_data = cursor.fetchone()
            # all_device_cnt = all_devices_cnt_data['all_device_cnt']
            # print("3️⃣平台总设备数：", all_device_cnt)
            #
            # cursor.execute(query_platform_add_devices_cnt)
            # add_devices_cnt = cursor.fetchone()
            # add_devices_cnt = add_devices_cnt['add_devices_cnt']
            # print("4️⃣平台本月新增设备数：", add_devices_cnt)

            cursor.execute(query_platform_all_projects_cnt)
            all_projects_cnt = cursor.fetchone()
            all_projects_cnt = all_projects_cnt['all_projects_cnt']
            print("5️⃣平台总项目数：", all_projects_cnt)

            cursor.execute(query_platform_add_projects_cnt)
            add_projects_cnt = cursor.fetchone()
            add_projects_cnt = add_projects_cnt['add_projects_cnt']
            print("6️⃣平台本月新增项目数：", add_projects_cnt)

            # cursor.execute(query_platform_project_city_cnt)
            # project_city_cnt = cursor.fetchone()
            # project_city_cnt = project_city_cnt['project_city_cnt']
            # print("7️⃣平台覆盖城市数：", project_city_cnt)

            # cursor.execute(query_charge_user_mau_cnt)
            # user_mau_cnt = cursor.fetchone()
            # user_mau_cnt = user_mau_cnt['user_mau_cnt']
            # print("8️⃣平台[小充]用户月活数：", user_mau_cnt)

        return render_template('ops_home_query.html',
                               next_month=next_month,
                               start_date=start_date,
                               end_date=end_date,
                               users_cnt=users_cnt,
                               users_add_cnt=users_add_cnt,
                               all_device_cnt=all_device_cnt,
                               add_devices_cnt=add_devices_cnt,
                               all_projects_cnt=all_projects_cnt,
                               add_projects_cnt=add_projects_cnt,
                               project_city_cnt=project_city_cnt,
                               user_mau_cnt=user_mau_cnt)
    except Exception as e:
        # 如果出现异常，可以返回一个错误页面或者 JSON 响应
        print(f"An error occurred: {e}")
        return jsonify({"error": "数据加载失败"}), 500


# todo 默认 5000端口
if __name__ == '__main__':
    app.run(debug=True)
