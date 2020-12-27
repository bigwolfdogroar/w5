#!/usr/bin/env python
# encoding:utf-8
from . import *


@r.route("/get/workflow/list", methods=['GET', 'POST'])
def get_user_list():
    if request.method == "POST":
        keywords = request.json.get("keywords", "")
        type = request.json.get("type", "0")

        workflow_list = Workflow.join(
            Users.__table__,
            Workflow.__table__ + '.user_id',
            '=',
            Users.__table__ + '.id'
        ).join(
            Types.__table__,
            Workflow.__table__ + '.type_id',
            '=',
            Types.__table__ + '.id'
        ).select(
            Workflow.__table__ + '.id',
            Workflow.__table__ + '.uuid',
            Workflow.__table__ + ".type_id",
            Workflow.__table__ + '.name',
            Workflow.__table__ + '.update_time',
            Workflow.__table__ + '.create_time',
            Users.__table__ + '.nick_name',
            Types.__table__ + '.name as type_name',
            Workflow.__table__ + '.remarks',
            Workflow.__table__ + '.status',
            Workflow.__table__ + '.timer_app',
            Workflow.__table__ + '.webhook_app',
            Workflow.__table__ + '.input_app',
        )

        if str(type) != "0":
            workflow_list = workflow_list.where(Workflow.__table__ + ".type_id", type)

        if str(keywords) == "":
            workflow_list = workflow_list.order_by(Workflow.__table__ + '.id', 'desc').get()
        else:
            workflow_list = workflow_list.where(
                Workflow.__table__ + '.name',
                'like',
                '%{keywords}%'.format(keywords=keywords)
            ).order_by(Workflow.__table__ + '.id', 'desc').get()

        return Response.re(data=workflow_list.serialize())


@r.route("/post/workflow/add", methods=['GET', 'POST'])
def post_workflow_add():
    if request.method == "POST":
        type = request.json.get("type", 0)

        uuid = Random.make_uuid()

        token = request.headers.get("token")
        user_id = redis.get(token)

        if type == 0:
            Workflow.insert({
                'uuid': str(uuid),
                "type_id": 1,
                "user_id": user_id,
                'name': "未命名",
                'start_app': "",
                'end_app': "",
                'input_app': "",
                'webhook_app': "",
                'timer_app': "",
                'flow_json': "",
                'flow_data': "",
                'controller_data': "",
                'local_var_data': "none",
                'remarks': "",
                'status': 0,
                'update_time': Time.get_date_time(),
                'create_time': Time.get_date_time()
            })
        elif type == 1:
            name = request.json.get("name", "")
            remarks = request.json.get("remarks", "")
            start_app = request.json.get("start_app", "")
            end_app = request.json.get("end_app", "")
            input_app = request.json.get("input_app", "")
            webhook_app = request.json.get("webhook_app", "")
            timer_app = request.json.get("timer_app", "")
            flow_json = request.json.get("flow_json", "")
            flow_data = request.json.get("flow_data", "")
            controller_data = request.json.get("controller_data", "")
            local_var_data = request.json.get("local_var_data", "")

            Workflow.insert({
                'uuid': str(uuid),
                "type_id": 1,
                "user_id": user_id,
                'name': name,
                'start_app': start_app,
                'end_app': end_app,
                'input_app': input_app,
                'webhook_app': webhook_app,
                'timer_app': timer_app,
                'flow_json': flow_json,
                'flow_data': flow_data,
                'controller_data': controller_data,
                'local_var_data': local_var_data,
                'remarks': remarks,
                'status': 0,
                'update_time': Time.get_date_time(),
                'create_time': Time.get_date_time()
            })

        return Response.re(data={"uuid": uuid})


@r.route("/post/workflow/detail", methods=['GET', 'POST'])
def get_workflow_detail():
    if request.method == "POST":
        uuid = request.json.get("uuid", "")

        workflow_info = Workflow.select(
            'uuid',
            'name',
            'start_app',
            'end_app',
            'input_app',
            'webhook_app',
            'timer_app',
            'flow_json',
            'flow_data',
            'controller_data',
            'type_id',
            'remarks',
            'local_var_data',
            'status'
        ).where("uuid", uuid).first()

        return Response.re(data=workflow_info.serialize())


@r.route("/post/workflow/update", methods=['GET', 'POST'])
def post_workflow_update():
    if request.method == "POST":
        uuid = request.json.get("uuid", "")
        name = request.json.get("name", "")
        start_app = request.json.get("start_app", "")
        end_app = request.json.get("end_app", "")
        input_app = request.json.get("input_app", "")
        webhook_app = request.json.get("webhook_app", "")
        timer_app = request.json.get("timer_app", "")
        flow_json = request.json.get("flow_json", "")
        flow_data = request.json.get("flow_data", "")
        controller_data = request.json.get("controller_data", "")
        type_id = request.json.get("type_id", "")
        remarks = request.json.get("remarks", "")
        local_var_data = request.json.get("local_var_data", "")

        if str(controller_data) != "{}":
            work_info = Workflow.select("timer_app").where('uuid', uuid).first()

            if work_info:
                if str(work_info.timer_app) == "" or str(work_info.timer_app) == "None" or work_info.timer_app is None:
                    w_timer_app = ""
                else:
                    w_timer_app = work_info.timer_app

                conn = rpyc.connect('localhost', 53124)
                conn.root.exec(uuid, timer_app, w_timer_app, controller_data)
                conn.close()
            else:
                return Response.re(err=ErrIsNotPlayBook)

        Workflow.where('uuid', uuid).update({
            'name': name,
            'start_app': start_app,
            'end_app': end_app,
            'input_app': input_app,
            'webhook_app': webhook_app,
            'timer_app': timer_app,
            'flow_json': flow_json,
            'flow_data': flow_data,
            'controller_data': controller_data,
            'type_id': type_id,
            'remarks': remarks,
            'local_var_data': local_var_data,
            'update_time': Time.get_date_time()
        })

        return Response.re()


@r.route("/post/workflow/del", methods=['GET', 'POST'])
def post_workflow_del():
    if request.method == "POST":
        uuid = request.json.get("uuid", "")

        work_info = Workflow.select("timer_app").where('uuid', uuid).first()

        if work_info:
            if str(work_info.timer_app) == "" or str(work_info.timer_app) == "None" or work_info.timer_app is None:
                pass
            else:
                conn = rpyc.connect('localhost', 53124)
                conn.root.remove(work_info.timer_app)
                conn.close()
        else:
            return Response.re(err=ErrIsNotPlayBook)

        Workflow.where('uuid', uuid).delete()
        return Response.re()


@r.route("/post/workflow/status", methods=['GET', 'POST'])
def post_workflow_status():
    if request.method == "POST":
        id = request.json.get("id", "")
        status = request.json.get("status", "")

        Workflow.where('id', id).update(
            {
                "status": status,
                "update_time": Time.get_date_time()
            }
        )

        return Response.re()


@r.route("/get/workflow/import_url", methods=['GET', 'POST'])
def post_workflow_import_url():
    if request.method == "POST":
        url = request.json.get("url", "")
        try:
            r = requests.get(url=url, timeout=10)
            return Response.re(data={"data": r.json()})
        except:
            return Response.re(err=ErrImportUrl)


@ws.route('/echo')
def echo_socket(s):
    while not s.closed:
        message = s.receive()

        if message:
            req_data = json.loads(message)
            method = req_data["method"]

            if method == "ping":
                pass
            elif method == "run":
                uuid = req_data["data"]["uuid"]
                auto_execute(uuid, s=s)
