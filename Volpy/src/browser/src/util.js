var logging = console.log

class bidict {
    constructor() {
        if (arguments.length == 0) {
            this.map = {};
        } else {
            this.map = arguments[0];
        }
        this.inverse = {};
        for (const key in this.map) {
            const val = this.map[key];
            this.inverse[val] = key;
        }
    }
    getMap() { return this.map }
    getRev() {return this.inverse }
    put(key, val) {
        this.map[key] = val;
        this.inverse[val] = key;
    }
    del(key) {
        let val = this.map[key];
        delete this.map[key]
        delete this.inverse[val];
    }
}

function UUIDGeneratorBrowser() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11)
        .replace(/[018]/g, c =>
            (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
        );
}

function generateDataRef() {
    return UUIDGeneratorBrowser();
}

class Status {
  static SUCCESS = 0;

  static EXECUTION_ERROR = 11;
  static SERIALIZATION_ERROR = 12;

  static DATA_NOT_FOUND = 21;
  static DATA_ON_OTHER = 22;

  static WORKER_BUSY = 31;
}

module.exports = {
    logging: logging,
    bidict: bidict,
    UUIDGeneratorBrowser: UUIDGeneratorBrowser,
    generateDataRef: generateDataRef,
    Status: Status
}