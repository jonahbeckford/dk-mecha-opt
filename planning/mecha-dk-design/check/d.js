const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1360,height:900}});await p.goto('file://'+process.argv[2]);
const h=await p.evaluate(()=>document.documentElement.scrollHeight);
await p.screenshot({path:process.argv[3],fullPage:true});console.log(h);await b.close();})();
