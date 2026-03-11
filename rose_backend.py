from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import uuid
import json
from extensions import db
# [修复] 引入 UserDevice
from models import RosaryData, DailyPrayer, UserDevice

rose_bp = Blueprint('rose', __name__, url_prefix='/api/rose')

@rose_bp.route('/handshake', methods=['POST'])
def rose_handshake():
    client_key = request.json.get('device_key')
    client_fp = request.json.get('fingerprint')
    client_data = request.json.get('data')
    legacy_id = request.json.get('legacy_id')
    client_ip = request.remote_addr

    # 1. 正常验证
    if client_key:
        user = UserDevice.query.get(client_key)
        if user:
            if user.fingerprint != client_fp: user.fingerprint = client_fp
            if client_data: user.data = client_data
            user.last_ip = client_ip
            db.session.commit()
            return jsonify({'status': 'verified', 'msg': '身份确认', 'data': user.data, 'name': user.device_name})

    # 2. 老用户迁移
    if legacy_id and not client_key:
        old_record = RosaryData.query.get(legacy_id)
        if old_record:
            new_uuid = 'u-' + str(uuid.uuid4())
            try:
                d = json.loads(old_record.data)
                u_name = d.get('userName', '老信徒')
            except: u_name = '老信徒'
            
            new_user = UserDevice(device_key=new_uuid, fingerprint=client_fp, device_name=u_name, data=old_record.data, last_ip=client_ip)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'status': 'migrated', 'new_key': new_uuid, 'data': old_record.data, 'name': u_name})

    # 3. 指纹找回
    if client_fp:
        candidate = UserDevice.query.filter_by(fingerprint=client_fp).order_by(UserDevice.updated_at.desc()).first()
        if candidate:
            return jsonify({'status': 'candidate_found', 'candidate_key': candidate.device_key, 'candidate_name': candidate.device_name, 'candidate_data': candidate.data})

    return jsonify({'status': 'new_user'})

@rose_bp.route('/register', methods=['POST'])
def rose_register():
    key = request.json.get('device_key')
    fp = request.json.get('fingerprint')
    name = request.json.get('device_name')
    data = request.json.get('data')
    if not key: return jsonify({'status': 'error'})
    
    user = UserDevice.query.get(key)
    if not user:
        user = UserDevice(device_key=key, fingerprint=fp, device_name=name, data=data, last_ip=request.remote_addr)
        db.session.add(user)
    else:
        user.device_name = name
        user.fingerprint = fp
        user.data = data
    db.session.commit()
    return jsonify({'status': 'success'})

@rose_bp.route('/sync', methods=['POST'])
# def rose_sync_simple():
#     # 简单的同步接口，复用 register 逻辑
#     return rose_register()
def rose_sync_upload():
    try:
        uid = request.json.get('uid'); data_str = request.json.get('data')
        if not uid or not data_str: return jsonify({'status': 'error', 'msg': '缺少参数'}), 400
        record = RosaryData.query.get(uid)
        if not record:
            record = RosaryData(uid=uid, data=data_str)
            db.session.add(record)
        else: record.data = data_str
        db.session.commit()
        return jsonify({'status': 'success', 'msg': '云端存档已更新'})
    except Exception as e: return jsonify({'status': 'error', 'msg': str(e)}), 500

@rose_bp.route('/sync/<uid>', methods=['GET'])
def rose_sync_download(uid):
    # 兼容旧逻辑
    record = RosaryData.query.get(uid)
    return jsonify({'status': 'success', 'data': record.data, 'time': record.updated_at}) if record else (jsonify({'status': 'error', 'msg': '未找到'}), 404)

@rose_bp.route('/prayers', methods=['GET'])
def get_prayers():
    try: # 清理过期数据
        DailyPrayer.query.filter(DailyPrayer.created_at < datetime.now() - timedelta(days=2)).delete()
        db.session.commit()
    except: db.session.rollback()
    
    offset = request.args.get('offset', 0, type=int)
    query = DailyPrayer.query.order_by(DailyPrayer.created_at.desc())
    total = query.count()
    prayers = query.offset(offset).limit(10).all()
    return jsonify({'status': 'success', 'data': [{'time': p.created_at.strftime('%H:%M'), 'name': p.name, 'content': p.content} for p in prayers], 'has_more': (offset + 10) < total})

@rose_bp.route('/prayer', methods=['POST'])
def submit_prayer():
    data = request.json
    content = data.get('content')
    if not content or len(content) < 5: return jsonify({'status': 'error', 'msg': '内容太短'}), 400
    db.session.add(DailyPrayer(uid=data.get('uid'), name=data.get('name'), content=content))
    db.session.commit()
    return jsonify({'status': 'success'})