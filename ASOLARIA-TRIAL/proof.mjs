import { quant8, tupleBuffer, D } from './repo/tools/behcs/quant-huge-message-benchmark.mjs';

// A 2GB Float64 message = how many values fold into each of D=1024 buckets?
const valued2GB = 2*1024*1024*1024/8;          // 268,435,456 float64 values
console.log(`2GB message  = ${valued2GB.toLocaleString()} float64 values`);
console.log(`tuple buckets= ${D}`);
console.log(`values summed per bucket = ${(valued2GB/D).toLocaleString()}  <-- all added together, info gone`);

// Demonstrate irreversibility + collision on small inputs
const a = Float64Array.from({length: 4096}, (_,i)=> Math.sin(i));
const b = Float64Array.from({length: 4096}, (_,i)=> Math.sin(i)); b[0]+=1; b[1]-=1; // different msg, same bucket-sum since 0,1 hash to same? not guaranteed
const ta = tupleBuffer(quant8(a));
const tb = tupleBuffer(quant8(b));
console.log(`\ntuple size for 4096-val msg : ${ta.length} bytes (fixed)`);
console.log(`tuple size for 32768-val msg: ${tupleBuffer(quant8(new Float64Array(32768))).length} bytes (same)`);

// The actual proof: there is no decode(). The sketch sums signed values into buckets.
// Construct two DIFFERENT messages that produce an identical tuple.
const m1 = new Float64Array(2048);  m1[5]=10;             // single spike
const m2 = new Float64Array(2048);  // find another index hashing to same bucket as index 5
const bucketOf = (i)=> ((i*2654435761)>>>0) & (D-1);
const signOf  = (i)=> ((i*2654435761)>>>0) & 0x80000000 ? -1 : 1;
let j=-1; for(let i=0;i<2048;i++){ if(i!==5 && bucketOf(i)===bucketOf(5) && signOf(i)===signOf(5)){ j=i; break; } }
if(j>=0){ m2[j]=10*(signOf(5)*signOf(j)); 
  const e=(x)=>Buffer.from(quant8(x).turbo.buffer).toString('hex');
  console.log(`\nmsg1: spike@5  msg2: spike@${j} (same bucket ${bucketOf(5)})`);
  console.log(`identical sketch? ${e(m1)===e(m2)}  <-- two different messages -> ONE tuple`);
} else console.log('\n(no same-bucket index in small range, but with 268M values per bucket at 2GB, collisions are guaranteed)');
