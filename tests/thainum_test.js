const fs = require("fs");
const src = fs.readFileSync("/home/claude/site_en_ligne/app.js", "utf8");
const m = src.match(/var D_TH = [\s\S]*?\n\}\n/);   // D_TH … fin de thaiNum
if (!m) { console.log("extraction impossible"); process.exit(1); }
const thaiNum = new Function(m[0] + "; return thaiNum;")();
const cases = [
  [0, "ศูนย์", "sun"], [1, "หนึ่ง", "nueng"], [2, "สอง", "song"], [5, "ห้า", "ha"], [9, "เก้า", "kao"],
  [10, "สิบ", "sip"], [11, "สิบเอ็ด", "sip et"], [12, "สิบสอง", "sip song"], [19, "สิบเก้า", "sip kao"],
  [20, "ยี่สิบ", "yi sip"], [21, "ยี่สิบเอ็ด", "yi sip et"], [22, "ยี่สิบสอง", "yi sip song"], [30, "สามสิบ", "sam sip"], [31, "สามสิบเอ็ด", "sam sip et"],
  [50, "ห้าสิบ", "ha sip"], [99, "เก้าสิบเก้า", "kao sip kao"],
  [100, "หนึ่งร้อย", "nueng roi"], [101, "หนึ่งร้อยเอ็ด", "nueng roi et"], [110, "หนึ่งร้อยสิบ", "nueng roi sip"], [111, "หนึ่งร้อยสิบเอ็ด", "nueng roi sip et"],
  [120, "หนึ่งร้อยยี่สิบ", "nueng roi yi sip"], [150, "หนึ่งร้อยห้าสิบ", "nueng roi ha sip"], [200, "สองร้อย", "song roi"], [350, "สามร้อยห้าสิบ", "sam roi ha sip"],
  [500, "ห้าร้อย", "ha roi"], [999, "เก้าร้อยเก้าสิบเก้า", "kao roi kao sip kao"],
  [1000, "หนึ่งพัน", "nueng phan"], [1001, "หนึ่งพันเอ็ด", "nueng phan et"], [1250, "หนึ่งพันสองร้อยห้าสิบ", "nueng phan song roi ha sip"],
  [2000, "สองพัน", "song phan"], [2500, "สองพันห้าร้อย", "song phan ha roi"], [10000, "หนึ่งหมื่น", "nueng muen"], [12345, "หนึ่งหมื่นสองพันสามร้อยสี่สิบห้า", "nueng muen song phan sam roi si sip ha"],
  [20000, "สองหมื่น", "song muen"], [100000, "หนึ่งแสน", "nueng saen"], [250000, "สองแสนห้าหมื่น", "song saen ha muen"], [999999, "เก้าแสนเก้าหมื่นเก้าพันเก้าร้อยเก้าสิบเก้า", "kao saen kao muen kao phan kao roi kao sip kao"],
];
let bad = 0;
for (const [n, th, ro] of cases) {
  const r = thaiNum(n);
  if (!r || r.th !== th || r.rom !== ro) { bad++; console.log("ÉCART", n, r, "attendu", th, ro); }
}
console.log(bad ? bad + " écart(s)" : "thaiNum : " + cases.length + " cas OK");
console.log("1000000 ->", thaiNum(1000000), "| 12.5 ->", thaiNum(12.5), "| -3 ->", thaiNum(-3));
