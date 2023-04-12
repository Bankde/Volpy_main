import autobahn from 'autobahn-browser';
import { bidict, logging } from './util.js';

export class SimpleWS {
   constructor(config) {
      this.connection = new autobahn.Connection({url: config["url"], realm: config["realm"]});
      this.connection.onopen = (session) => {
         this.session = session;
         this.onJoin(session);
      };
   }
      
   async onJoin(session) {
      if (this.id != null) {
         return;
      }
      this._session_id = session._id;
      logging(`Setup UUID: ${this.uuid}`);

      await session.subscribe('com.cluster.heartbeat', async (args) => {
         this._cluster_heartbeat_d(args)
      });
      this.id = await session.call('com.node.register', [ this._session_id, this.uuid ]);
      await session.register(`com.node${this.id}.call`, async (args) => {
         return await this.recv(args);
      });
      logging(`Setup Node finish: sid_${this._session_id} id_${this.id}`);
   }

   async _cluster_heartbeat_d(args) {
      /*
      Params: data of id2uuid
      Return: None
      */
      let [ data ] = args;
      let set_id2uuid = data["id2uuid"];
      this.id2uuid = new bidict(set_id2uuid);
   }

   setCallback(t, callback) {
      this.callback[t] = callback;
   }

   async recv(args) {
      /*
      Params: msg: object
      Return: ret: object
      */
      let [ msg ] = args;
      // logging(`${this.id} recv: ${msg}`);
      let { msgType, data } = msg;
      if (!(msgType in this.callback)) {
         throw new Error("MsgType not implement");
      }
      let f = this.callback[msgType];
      let ret_obj = await f(data);
      return ret_obj;
   }

   async send(id, msgType, data) {
      let msg = { "msgType": msgType, "data": data };
      let t = await this.session.call(`com.node${id}.call`, [ msg ]);
      return t;
   }

   async broadcast(msgType, data) {
      // logging(`${this.id} broadcast: ${data}`);
      let msg = { "msgType": msgType, "data": data };
      let tasks = [];
      for (const id in this.id2uuid.getMap()) {
         if (id == this.id) {
            continue;
         }
         let t = this.session.call(`com.node${id}.call`, [ msg ]);
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
      this.uuid = uuid;
      this.id = null;
      this.callback = {};
      this.heartbeat = {};
      this.callback["0"] = function (x) { x };
   }
}