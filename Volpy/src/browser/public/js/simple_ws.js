try {
   // for Node.js
   var autobahn = require('autobahn');
} catch (e) {
   // for browsers (where AutobahnJS is available globally)
   var autobahn = window.autobahn;
}

import { bidict, logging } from './util.js';

export class SimpleWS {
   constructor(config) {
      this.connection = new autobahn.Connection({url: config["url"], realm: config["realm"]});
      this.connection.onopen = async function (session) {
         if (this.id != null) {
            return;
         }
         this._session_id = session.id
         logging(`Setup UUID: ${this.uuid}`);

         await session.subscribe(this._cluster_heartbeat_d, 'com.cluster.heartbeat');
         this.id = await session.call('com.node.register', this._session_id, this.uuid);
         await session.register(this.recv, `com.node${this.id}.call`);
         logging(`Setup Node finish: sid_${this._session_id} id_${this.id}`)
      };
   }

   async _node_register_d(sid, uuid) {
      /*
      Return new node id (str)
      */
      if (uuid in this.id2uuid.getRev()) {
         let id = this.id2uuid.getRev()[uuid];
         return id;
      } else {
         // Generate id for node
         let id = str(this.id2uuid.getMap().length);
         this.id2uuid.put(id, uuid);
         this.id2sid.put(id, sid);
         logging(`Reg: ${id}, ${sid}`)
         await this._cluster_update_call();
         return id;
      }
   }

   async _node_unregister_d(sid) {
      if (sid in this.id2sid.getRev()) {
         let id = this.id2sid.getRev()[sid];
         logging(`Unreg: ${id}, ${sid}`);
         this.id2uuid.del(id);
         this.id2sid.del(id);
         await this._cluster_update_call();
      }
   }

   async _cluster_update_call() {
      let id2uuid_map = self.id2uuid.getMap();
      let data = {"id2uuid": JSON.stringify(id2uuid_map)};
      this.publish('com.cluster.heartbeat', data);
   }

   async _cluster_heartbeat_d(data) {
      let id2uuid_map = JSON.parse(data["id2uuid"]);
      this.id2uuid = new bidict(id2uuid_map);
   }

   setCallback(t, callback) {
      this.callback[t] = callback;
   }

   async recv(msg) {
      logging(`${this.id} recv: ${msg}`);
      let { msgType, data } = msg;
      if (!(msgType in this.callback)) {
         throw new Error("MsgType not implement");
      }
      let f = this.callback[msgType];
      let ret_obj = await f(data);
      return ret_obj;
   }

   async send(id, msgType, data) {
      if (!(msgType in this.callback)) {
         throw new Error("MsgType not implement");
      }
      let msg = { "msgType": msgType, "data": data };
      let t = await this.call(`com.node${id}.call`, msg);
      return t;
   }

   async broadcast(msgType, data) {
      logging(`${this.id} broadcast: ${data}`);
      if (!(msgType in this.callback)) {
         throw new Error("MsgType not implemented");
      }
      let msg = { "msgType": msgType, "data": data };
      let tasks = [];
      for (const id in this.id2uuid.getMap()) {
         if (id == this.id) {
            continue;
         }
         t = this.call(`com.node${id}.call`, msg);
         tasks.push(t);
      }
      let ts = await Promise.all(tasks);
      return ts;
   }

   getId() {
      return this.id;
   }

   getMainId() {
      return "0";
   }

   start() {
      this.connection.open();
   }

   init(uuid) {
      this.is_main = false;
      this.id2uuid = new bidict();
      this.id2sid = new bidict();
      this.heartbeatlist = {};
      this.uuid = uuid
      this.id = null
      this.callback = {}
      this.heartbeat = {}
      this.callback["0"] = function (x) { x }
   }
}