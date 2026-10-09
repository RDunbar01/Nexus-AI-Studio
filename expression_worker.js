globalThis.NexusPretrainedAssets={"schemaVersion":"nexus-pretrained-assets-v1","runtime":{"name":"onnxruntime-web","version":"1.22.0","license":"MIT","sourceUrl":"https://registry.npmjs.org/onnxruntime-web/-/onnxruntime-web-1.22.0.tgz","files":{"ort-wasm-simd-threaded.mjs":{"path":"assets/runtime/ort-wasm-simd-threaded.mjs","bytes":20856,"sha256":"30dd851d9c00622940500f71ddd2ff8820c5cb65270816080175b958705385a8"},"ort-wasm-simd-threaded.wasm":{"path":"assets/runtime/ort-wasm-simd-threaded.wasm","bytes":11210254,"sha256":"71aef04959c5c1b6de461b6538e2058e306610034a85aad2742d0c7fd4533fe4"},"ort.wasm.min.mjs":{"path":"assets/runtime/ort.wasm.min.mjs","bytes":48259,"sha256":"6ef726f355b791129f7ddf3f62e7877a16b9b777abe87004b8ab306e6b9cf265"}},"packageSha256":"e293551f9d36d003e293d0f2937fee7b3dfdcef76d71d1449b55e2d4157c7aea","npmIntegrity":"sha512-Ud/+EBo6mhuaQWt/OjaOk0iNWjXqJoeeMFr6xQEERZdIZH2OWpGzuujz7lfuOBjUa6TEE/sc4nb7Da5dNL34fg=="},"models":{"detection":{"path":"assets/models/face_detection_yunet_2023mar.onnx","bytes":232589,"sha256":"8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4","name":"YuNet","identity":{"backendId":"opencv-zoo-yunet-onnx-v1","adapterVersion":"nexus-pretrained-v1","modelSha256":"8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4","preprocessingVersion":"yunet-bgr640-letterbox-v1","task":"detection"},"sourceUrl":"https://media.githubusercontent.com/media/opencv/opencv_zoo/f12e12798e8314f7c074a6656816c048dcc95b7a/models/face_detection_yunet/face_detection_yunet_2023mar.onnx","immutableRevision":"f12e12798e8314f7c074a6656816c048dcc95b7a","weightLicense":"MIT","runtimeLicense":"MIT","licenseEvidenceUrl":"https://raw.githubusercontent.com/opencv/opencv_zoo/f12e12798e8314f7c074a6656816c048dcc95b7a/models/face_detection_yunet/LICENSE","trainingDataStatus":"Unresolved exact training-set and rights provenance; not cleared for unrestricted deployment.","restrictions":["Directory/file licensing evidence is not blanket commercial, military, biometric privacy, or training-data clearance.","Experimental consented local development only; no authentication, security unlock, diagnosis, or internal-emotion claims."],"inputName":"input","inputShape":[1,3,640,640],"outputName":null,"inputSpec":"[1, 3, 640, 640]","outputSpec":"12 tensors: cls/obj/bbox/kps at strides 8,16,32"},"expression":{"path":"assets/models/facial_expression_recognition_mobilefacenet_2022july.onnx","bytes":4791892,"sha256":"4f61307602fc089ce20488a31d4e4614e3c9753a7d6c41578c854858b183e1a9","name":"ProgressiveTeacherFER","identity":{"backendId":"opencv-zoo-progressiveteacherfer-onnx-v1","adapterVersion":"nexus-pretrained-v1","modelSha256":"4f61307602fc089ce20488a31d4e4614e3c9753a7d6c41578c854858b183e1a9","preprocessingVersion":"fer-rgb112-inverse-similarity-minus1to1-v1","task":"expression"},"sourceUrl":"https://huggingface.co/opencv/facial_expression_recognition/resolve/cc14b308d84bae302497477d202314a3348addf7/facial_expression_recognition_mobilefacenet_2022july.onnx","immutableRevision":"cc14b308d84bae302497477d202314a3348addf7","weightLicense":"Apache-2.0","runtimeLicense":"MIT","licenseEvidenceUrl":"https://huggingface.co/opencv/facial_expression_recognition/blob/cc14b308d84bae302497477d202314a3348addf7/README.md","trainingDataStatus":"Unresolved exact training-set and rights provenance; not cleared for unrestricted deployment.","restrictions":["Directory/file licensing evidence is not blanket commercial, military, biometric privacy, or training-data clearance.","Experimental consented local development only; no authentication, security unlock, diagnosis, or internal-emotion claims."],"inputName":"data","inputShape":[1,3,112,112],"outputName":"label","inputSpec":"[1, 3, 112, 112]","outputSpec":"label [1,7] logits; adapter softmax gives model scores","labels":["angry","disgust","fearful","happy","neutral","sad","surprised"]}}};
/* Nexus pretrained inference adapter. No camera, persistence, provider, or download service.
 * Model/runtime notices and upstream algorithm references: docs/PRETRAINED_RUNTIME.md.
 */
(function(root,factory){
  if(typeof module==='object'&&module.exports)module.exports=factory(require('./manifest.json'));
  else root.NexusPretrainedVision=factory(root.NexusPretrainedAssets);
})(typeof globalThis!=='undefined'?globalThis:this,function(DEFAULT_MANIFEST){
  'use strict';
  const TASKS=['detection','expression'];
  const SIZE=640, FACE_SIZE=112;
  const LANDMARK_KINDS=['right_eye','left_eye','nose_tip','right_mouth_corner','left_mouth_corner'];
  const STANDARD_POINTS=[[38.2946,51.6963],[73.5318,51.5014],[56.0252,71.7366],[41.5493,92.3655],[70.7299,92.2041]];
  function fail(code,message){const e=new Error(message||code);e.code=code;throw e;}
  function finite(value){return Number.isFinite(value);}
  function clamp(x,a,b){return Math.max(a,Math.min(b,x));}
  function token(frame){return {requestId:frame.requestId,epoch:frame.epoch,capturedAt:frame.capturedAt,roiRevision:frame.roiRevision};}
  function validateFrame(frame){
    if(!frame||!Number.isInteger(frame.width)||!Number.isInteger(frame.height)||frame.width<1||frame.height<1||frame.width>4096||frame.height>4096||frame.width*frame.height>16777216)fail('invalid_frame_dimensions');
    if(!(frame.pixels instanceof Uint8Array||frame.pixels instanceof Uint8ClampedArray)||frame.pixels.length!==frame.width*frame.height*4)fail('invalid_rgba_pixels');
    if(typeof frame.requestId!=='string'||!frame.requestId||!Number.isSafeInteger(frame.epoch)||frame.epoch<0||!finite(frame.capturedAt)||!Number.isSafeInteger(frame.roiRevision)||frame.roiRevision<0)fail('invalid_frame_token');
    return frame;
  }
  function bytes(value){
    if(value instanceof ArrayBuffer)return new Uint8Array(value);
    if(value instanceof Uint8Array)return value;
    fail('invalid_asset_bytes');
  }
  async function sha256(value,cryptoImpl){
    const c=cryptoImpl||(typeof globalThis!=='undefined'&&globalThis.crypto);
    if(!c||!c.subtle)fail('secure_hash_unavailable','SHA-256 verification requires Web Crypto.');
    const digest=await c.subtle.digest('SHA-256',bytes(value));
    return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
  }
  async function verifyAsset(value,spec,cryptoImpl){
    value=bytes(value);
    if(!spec||!Number.isSafeInteger(spec.bytes)||!/^[a-f0-9]{64}$/.test(spec.sha256))fail('invalid_asset_manifest');
    if(value.length!==spec.bytes)fail('asset_size_mismatch',spec.path+' has an unexpected byte length.');
    if(await sha256(value,cryptoImpl)!==spec.sha256)fail('asset_hash_mismatch',spec.path+' failed SHA-256 verification.');
    return value;
  }
  /** Only same-origin local app assets, with redirects prohibited. Injected asset readers
   * are trusted host dependencies and must obey the same no-remote/no-frame-upload rule. */
  function createLocalAssetReader(options){
    options=options||{};
    const location=options.location||(typeof globalThis!=='undefined'&&globalThis.location);
    const base=new URL(options.baseUrl||'./',location&&location.href);
    if(!location||base.origin!==location.origin||!['http:','https:'].includes(base.protocol)||base.username||base.password)fail('same_origin_assets_required');
    const fetchImpl=options.fetchImpl||globalThis.fetch;
    if(typeof fetchImpl!=='function')fail('local_fetch_unavailable');
    return async function(path){
      if(typeof path!=='string'||!/^assets\/(models|runtime)\/[a-zA-Z0-9._-]+$/.test(path))fail('invalid_asset_path');
      const url=new URL(path,base);
      if(url.origin!==base.origin)fail('same_origin_assets_required');
      const response=await fetchImpl(url.href,{method:'GET',credentials:'omit',redirect:'error',cache:'no-store',referrerPolicy:'no-referrer'});
      if(!response.ok)fail('local_asset_unavailable','Local asset '+path+' returned HTTP '+response.status+'.');
      if(response.url&&new URL(response.url).origin!==base.origin)fail('asset_redirect_forbidden');
      return new Uint8Array(await response.arrayBuffer());
    };
  }
  /** Browser-only loader. Verifies every executable byte before import; the runtime gets
   * a verified in-memory WASM binary and a verified Blob module, never a CDN fallback.
   * Keep its blob URLs alive until all backend sessions have been disposed. */
  async function loadVerifiedRuntime(options){
    options=options||{};
    const supplied=options.manifest||DEFAULT_MANIFEST;
    if(!supplied||!supplied.runtime||supplied.runtime.name!=='onnxruntime-web'||supplied.runtime.version!=='1.22.0')fail('unsupported_runtime_manifest');
    for(const [name,expected] of Object.entries(DEFAULT_MANIFEST.runtime.files)){const spec=supplied.runtime.files&&supplied.runtime.files[name];if(!spec||spec.sha256!==expected.sha256||spec.bytes!==expected.bytes||spec.path!==expected.path)fail('unsupported_runtime_manifest');}
    const manifest=JSON.parse(JSON.stringify(supplied));
    const read=options.assetReader||createLocalAssetReader(options);
    const wantsGpu=false;
    const names=['ort.wasm.min.mjs','ort-wasm-simd-threaded.mjs','ort-wasm-simd-threaded.wasm'];
    const verified=[];
    for(const name of names){const spec=manifest.runtime.files[name];verified.push(await verifyAsset(await read(spec.path),spec,options.crypto));}
    const urls=[];
    try{
      const makeModule=data=>{const url=URL.createObjectURL(new Blob([data],{type:'text/javascript'}));urls.push(url);return url;};
      const entry=makeModule(verified[0]),engine=makeModule(verified[1]);
      // ORT 1.22 omits locateFile when wasmBinary is present, but its Emscripten
      // engine still resolves a relative WASM name against import.meta.url.
      // Blob URLs cannot serve as that base. Keep every vendor byte unchanged:
      // this application-owned module supplies a bounded locator directly to
      // the verified engine, pointing only at the already verified WASM Blob.
      const binary=URL.createObjectURL(new Blob([verified[2]],{type:'application/wasm'}));urls.push(binary);
      const engineAdapter=makeModule('import createEngine from '+JSON.stringify(engine)+';\n'+
        'export default function(options){return createEngine({...options,locateFile(name){'+
        'if(name!=='+JSON.stringify(names[2])+')throw new Error("unverified_runtime_asset");'+
        'return '+JSON.stringify(binary)+';}});}\n');
      const ort=await import(entry);
      if(ort.env.versions.web!=='1.22.0')fail('runtime_version_mismatch');
      ort.env.wasm.numThreads=1;
      ort.env.wasm.proxy=false;
      ort.env.wasm.wasmPaths={mjs:engineAdapter};
      ort.env.wasm.wasmBinary=verified[2];
      return {ort,assetReader:read,manifest,executionProvider:wantsGpu?'auto':'wasm',verification:'sha256_all_runtime_bytes',release(){for(const url of urls)URL.revokeObjectURL(url);urls.length=0;}};
    }catch(error){for(const url of urls)URL.revokeObjectURL(url);throw error;}
  }
  function pixel(frame,x,y,c,border){
    if(border==='clamp'){x=clamp(x,0,frame.width-1);y=clamp(y,0,frame.height-1);}
    else if(x<0||y<0||x>=frame.width||y>=frame.height)return 0;
    return frame.pixels[(y*frame.width+x)*4+c];
  }
  function bilinear(frame,x,y,c,border){
    const x0=Math.floor(x),y0=Math.floor(y),dx=x-x0,dy=y-y0;
    return (1-dy)*((1-dx)*pixel(frame,x0,y0,c,border)+dx*pixel(frame,x0+1,y0,c,border))+dy*((1-dx)*pixel(frame,x0,y0+1,c,border)+dx*pixel(frame,x0+1,y0+1,c,border));
  }
  function prepareDetection(frame){
    validateFrame(frame);
    const scale=SIZE/Math.max(frame.width,frame.height),width=Math.max(1,Math.round(frame.width*scale)),height=Math.max(1,Math.round(frame.height*scale));
    const scaleX=width/frame.width,scaleY=height/frame.height,plane=SIZE*SIZE,data=new Float32Array(3*plane);
    for(let y=0;y<height;y++)for(let x=0;x<width;x++)for(let c=0;c<3;c++)data[c*plane+y*SIZE+x]=Math.round(bilinear(frame,(x+.5)/scaleX-.5,(y+.5)/scaleY-.5,2-c,'clamp'));
    return {data,dims:[1,3,SIZE,SIZE],geometry:{width,height,scaleX,scaleY,frameWidth:frame.width,frameHeight:frame.height}};
  }
  function iou(a,b){const w=Math.max(0,Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)),h=Math.max(0,Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)),intersection=w*h;return intersection/(a.width*a.height+b.width*b.height-intersection||1);}
  function tensorValues(outputs,name,length){
    const t=outputs[name];
    if(!t||!t.data||t.data.length!==length||t.type&&t.type!=='float32'||!Array.from(t.data).every(finite))fail('invalid_model_output',name+' has an invalid shape, type, or numeric value.');
    return t.data;
  }
  function decodeYuNet(outputs,geometry,options){
    options=options||{};const threshold=options.scoreThreshold==null?.9:options.scoreThreshold,nms=options.nmsThreshold==null?.3:options.nmsThreshold;
    if(!finite(threshold)||threshold<=0||threshold>1||!finite(nms)||nms<0||nms>1)fail('invalid_detector_threshold');
    const faces=[];
    for(const stride of [8,16,32]){
      const cols=SIZE/stride,n=cols*cols,cls=tensorValues(outputs,'cls_'+stride,n),obj=tensorValues(outputs,'obj_'+stride,n),bbox=tensorValues(outputs,'bbox_'+stride,n*4),kps=tensorValues(outputs,'kps_'+stride,n*10);
      for(let i=0;i<n;i++){
        const score=Math.sqrt(clamp(cls[i],0,1)*clamp(obj[i],0,1));if(score<threshold)continue;
        const col=i%cols,row=Math.floor(i/cols),w=Math.exp(bbox[i*4+2])*stride,h=Math.exp(bbox[i*4+3])*stride;
        const cx=(col+bbox[i*4])*stride,cy=(row+bbox[i*4+1])*stride;
        if(![cx,cy,w,h].every(finite)||w<=0||h<=0)continue;
        if(cx<0||cy<0||cx>=geometry.width||cy>=geometry.height)continue;
        const face={x:(cx-w/2)/geometry.scaleX,y:(cy-h/2)/geometry.scaleY,width:w/geometry.scaleX,height:h/geometry.scaleY,score,source:'model_detector',landmarks:[]};
        for(let j=0;j<5;j++)face.landmarks.push({x:(col+kps[i*10+j*2])*stride/geometry.scaleX,y:(row+kps[i*10+j*2+1])*stride/geometry.scaleY,kind:LANDMARK_KINDS[j]});
        faces.push(face);
      }
    }
    faces.sort((a,b)=>b.score-a.score);
    const selected=[];
    for(const face of faces.slice(0,5000))if(!selected.some(other=>iou(face,other)>nms))selected.push(face);
    return selected;
  }
  // Least-squares, orientation-preserving similarity: [a,-b,tx;b,a,ty].
  function similarity(from,to){
    if(!Array.isArray(from)||from.length!==5||!Array.isArray(to)||to.length!==5||![...from.flat(),...to.flat()].every(finite))fail('invalid_landmarks');
    const sx=from.reduce((a,p)=>a+p[0],0)/5,sy=from.reduce((a,p)=>a+p[1],0)/5,dx=to.reduce((a,p)=>a+p[0],0)/5,dy=to.reduce((a,p)=>a+p[1],0)/5;
    let den=0,aa=0,bb=0;
    for(let i=0;i<5;i++){const x=from[i][0]-sx,y=from[i][1]-sy,u=to[i][0]-dx,v=to[i][1]-dy;den+=x*x+y*y;aa+=x*u+y*v;bb+=x*v-y*u;}
    if(den<1e-8)fail('degenerate_landmarks');
    const a=aa/den,b=bb/den;
    if(!finite(a)||!finite(b)||a*a+b*b<1e-12)fail('degenerate_landmarks');
    return [a,-b,dx-a*sx+b*sy,b,a,dy-b*sx-a*sy];
  }
  function inverseAffine(m){const det=m[0]*m[4]-m[1]*m[3];if(!finite(det)||Math.abs(det)<1e-12)fail('degenerate_landmarks');return [m[4]/det,-m[1]/det,(m[1]*m[5]-m[4]*m[2])/det,-m[3]/det,m[0]/det,(m[3]*m[2]-m[0]*m[5])/det];}
  function prepareFace(frame,region,purpose){
    validateFrame(frame);if(purpose!=='expression')fail('invalid_purpose');
    if(!region||!Array.isArray(region.landmarks)||region.landmarks.length!==5)fail('five_landmarks_required');
    const points=region.landmarks.map((p,i)=>{if(!p||p.kind!==LANDMARK_KINDS[i]||!finite(p.x)||!finite(p.y))fail('invalid_landmark_order');return [p.x,p.y];});
    // Upstream FER solves destination-to-source for the aligned 112px crop.
    const warp=similarity(STANDARD_POINTS,points);
    const plane=FACE_SIZE*FACE_SIZE,data=new Float32Array(plane*3);
    for(let y=0;y<FACE_SIZE;y++)for(let x=0;x<FACE_SIZE;x++){
      const u=warp[0]*x+warp[1]*y+warp[2],v=warp[3]*x+warp[4]*y+warp[5];
      for(let c=0;c<3;c++){const value=Math.round(clamp(bilinear(frame,u,v,c,'zero'),0,255));data[c*plane+y*FACE_SIZE+x]=(value/255-.5)/.5;}
    }
    return {data,dims:[1,3,FACE_SIZE,FACE_SIZE]};
  }
  function assessFaceQuality(frame,region,prepared,purpose){
    const checks={opaque:true,regionSize:false,visibleRegion:false,landmarks:false,exposure:false,contrast:false,texture:false};
    for(let i=3;i<frame.pixels.length;i+=4)if(frame.pixels[i]!==255){checks.opaque=false;break;}
    const points=region&&region.landmarks||[],w=region&&region.width,h=region&&region.height;
    checks.regionSize=finite(w)&&finite(h)&&w>=32&&h>=32;
    if(checks.regionSize){const visible=Math.max(0,Math.min(frame.width,region.x+w)-Math.max(0,region.x))*Math.max(0,Math.min(frame.height,region.y+h)-Math.max(0,region.y));checks.visibleRegion=visible/(w*h)>=.7;}
    checks.landmarks=points.length===5&&points.every((p,i)=>p.kind===LANDMARK_KINDS[i]&&finite(p.x)&&finite(p.y)&&p.x>=0&&p.y>=0&&p.x<frame.width&&p.y<frame.height);
    if(checks.landmarks){const eyes=Math.hypot(points[1].x-points[0].x,points[1].y-points[0].y),mouth=Math.hypot(points[4].x-points[3].x,points[4].y-points[3].y);checks.landmarks=eyes>=5&&mouth>=4&&(points[3].y+points[4].y-points[0].y-points[1].y)/2>=4;}
    const plane=FACE_SIZE*FACE_SIZE,lum=new Float32Array(plane);let sum=0,sq=0,gradient=0;
    for(let i=0;i<plane;i++){let r=prepared.data[i],g=prepared.data[plane+i],b=prepared.data[2*plane+i];if(purpose==='expression'){r=(r+1)*127.5;g=(g+1)*127.5;b=(b+1)*127.5;}const value=.2126*r+.7152*g+.0722*b;lum[i]=value;sum+=value;sq+=value*value;}
    const mean=sum/plane,std=Math.sqrt(Math.max(0,sq/plane-mean*mean));
    for(let y=1;y<FACE_SIZE;y++)for(let x=1;x<FACE_SIZE;x++){const i=y*FACE_SIZE+x;gradient+=Math.abs(lum[i]-lum[i-1])+Math.abs(lum[i]-lum[i-FACE_SIZE]);}
    const texture=gradient/(2*(FACE_SIZE-1)*(FACE_SIZE-1));checks.exposure=mean>=12&&mean<=243;checks.contrast=std>=6;checks.texture=texture>=1.5;
    const failed=Object.keys(checks).filter(k=>!checks[k]);
    return {usable:failed.length===0,reason:failed.length?'quality_'+failed.join('_'):'heuristic_quality_pass',checks,meanLuminance:mean,luminanceStd:std,meanGradient:texture,heuristic:true,faceQualityValidated:false};
  }
  function softmax(raw){const values=Array.from(raw);if(values.length!==7||!values.every(finite))fail('invalid_expression_logits');const max=Math.max(...values),exp=values.map(x=>Math.exp(x-max)),sum=exp.reduce((a,b)=>a+b,0);return exp.map(x=>x/sum);}
  function createPretrainedBackend(options){
    options=options||{};const ort=options.ort,suppliedManifest=options.manifest||DEFAULT_MANIFEST;
    if(!ort||!ort.InferenceSession||!ort.Tensor)fail('onnx_runtime_required');
    if(!suppliedManifest||suppliedManifest.schemaVersion!=='nexus-pretrained-assets-v1')fail('invalid_manifest');
    // This adapter implements these exact graph contracts. A new artifact requires a
    // deliberate adapter/registry revision, never relabeling an existing session.
    for(const task of TASKS){
      const spec=suppliedManifest.models&&suppliedManifest.models[task],expected=DEFAULT_MANIFEST&&DEFAULT_MANIFEST.models[task];
      if(!spec||!expected||spec.sha256!==expected.sha256||spec.bytes!==expected.bytes||spec.inputName!==expected.inputName||spec.outputName!==expected.outputName||JSON.stringify(spec.inputShape)!==JSON.stringify(expected.inputShape)||!spec.identity||Object.keys(expected.identity).some(key=>spec.identity[key]!==expected.identity[key])||task==='expression'&&JSON.stringify(spec.labels)!==JSON.stringify(expected.labels))fail('unsupported_model_manifest');
    }
    const manifest=JSON.parse(JSON.stringify(suppliedManifest));
    const read=options.assetReader||createLocalAssetReader(options);
    const provider=options.executionProvider||'wasm';if(provider!=='wasm')fail('invalid_execution_provider');
    const sessions={},pending={},states={};for(const task of TASKS)states[task]={readiness:'not_loaded',executionProvider:null,error:null};
    let destroyed=false,lifecycle=0,busy=false,activeDone=null,finishActive=null,disposal=null;
    function alive(){if(destroyed)fail('backend_disposed');}
    function current(opts,version){return !destroyed&&version===lifecycle&&!(opts.signal&&opts.signal.aborted)&&(!opts.isCurrent||opts.isCurrent());}
    function base(task,frame,status,reason){return {...token(frame),identity:{...manifest.models[task].identity},status,reason};}
    function empty(task,frame,status,reason){const value=base(task,frame,status,reason);if(task==='detection')return {...value,regions:[]};return {...value,features:null,labels:[...manifest.models.expression.labels],scores:null,scoreType:'unavailable',establishesInternalEmotion:false};}
    async function loadOne(task){
      alive();if(sessions[task])return;if(pending[task])return pending[task];
      const version=lifecycle;states[task]={readiness:'loading',executionProvider:null,error:null};
      pending[task]=(async()=>{
        let session;
        try{
          const spec=manifest.models[task],data=await verifyAsset(await read(spec.path),spec,options.crypto);
          if(destroyed||version!==lifecycle)fail('backend_disposed');
          const available=options.gpuAvailable==null?!!(globalThis.navigator&&globalThis.navigator.gpu):options.gpuAvailable;
          let selected='wasm',fallback=null;
          if(provider!=='wasm'&&available){
            try{session=await ort.InferenceSession.create(data,{executionProviders:['webgpu','wasm'],logSeverityLevel:3});selected='webgpu_requested_with_wasm_fallback';}
            catch(error){fallback='WebGPU session failed: '+(error.code||String(error).slice(0,180));}
          }else if(provider==='webgpu')fallback='WebGPU is unavailable; using WASM CPU.';
          if(!session)session=await ort.InferenceSession.create(data,{executionProviders:['wasm'],logSeverityLevel:3});
          const input=session.inputMetadata&&session.inputMetadata[0];
          if(session.inputNames.length!==1||session.inputNames[0]!==spec.inputName||input&&(input.type!=='float32'||JSON.stringify(input.shape)!==JSON.stringify(spec.inputShape)))fail('model_input_contract_mismatch');
          if(spec.outputName&&!session.outputNames.includes(spec.outputName))fail('model_output_contract_mismatch');
          if(destroyed||version!==lifecycle)fail('backend_disposed');
          sessions[task]=session;states[task]={readiness:'ready',executionProvider:selected,error:null,fallbackReason:fallback};
        }catch(error){if(session)await session.release();states[task]={readiness:'error',executionProvider:null,error:error.code||String(error)};throw error;}
        finally{delete pending[task];}
      })();return pending[task];
    }
    async function load(tasks){
      alive();tasks=tasks||{};
      // Sequential initialization: ORT's single WASM instance rejects concurrent init.
      await loadOne('detection');
      for(const task of ['expression'])if(tasks[task]===true)await loadOne(task);
      return getStatus();
    }
    function getStatus(){return {name:'YuNet + Progressive Teacher FER (expression only)',state:destroyed?'disposed':states.detection.readiness,automaticDetection:!destroyed&&states.detection.readiness==='ready',captureProfileId:'yunet640-fivepoint-unmirrored-v1',tasks:JSON.parse(JSON.stringify(states)),modelIdentities:Object.fromEntries(TASKS.map(t=>[t,{...manifest.models[t].identity}])),runtimeVersion:ort.env&&ort.env.versions&&ort.env.versions.web||'injected_unverified',accuracyValidated:false,fineTuned:false};}
    async function run(task,prepared){
      const tensor=new ort.Tensor('float32',prepared.data,prepared.dims);let outputs;
      try{outputs=await sessions[task].run({[manifest.models[task].inputName]:tensor});return outputs;}
      finally{if(typeof tensor.dispose==='function')tensor.dispose();prepared.data.fill(0);}
    }
    function releaseOutputs(outputs){if(outputs)for(const output of Object.values(outputs))if(typeof output.dispose==='function')output.dispose();}
    async function analyzeFrame(frame,opts){
      alive();validateFrame(frame);opts=opts||{};
      const flags={expression:opts.expressionEnabled===true},version=lifecycle;
      const result={frameSize:{width:frame.width,height:frame.height},detection:empty('detection',frame,'unknown','disabled'),expression:empty('expression',frame,'unknown',flags.expression?'not_run':'disabled')};
      if(!flags.expression)return result;
      if(busy){for(const task of TASKS)if(task==='detection'||flags[task])result[task]=empty(task,frame,'unknown','busy');return result;}
      if(!current(opts,version)){for(const task of TASKS)if(task==='detection'||flags[task])result[task]=empty(task,frame,'unknown','stale_frame');return result;}
      if(!sessions.detection){for(const task of TASKS)if(task==='detection'||flags[task])result[task]=empty(task,frame,'unavailable','model_not_loaded');return result;}
      busy=true;activeDone=new Promise(resolve=>{finishActive=resolve;});
      try{
        let outputs;
        try{
          const prepared=prepareDetection(frame);outputs=await run('detection',prepared);
          if(!current(opts,version))return staleResult();
          const regions=decodeYuNet(outputs,prepared.geometry,options);
          result.detection={...base('detection',frame,'ok',regions.length?'faces_detected':'no_face'),regions};
        }finally{releaseOutputs(outputs);}
        if(result.detection.regions.length!==1){const reason=result.detection.regions.length?'multiple_faces':'no_face';for(const task of ['expression'])if(flags[task])result[task]=empty(task,frame,'unknown',reason);return result;}
        const region=result.detection.regions[0];
        for(const task of ['expression']){
          if(!flags[task])continue;
          if(!current(opts,version))return staleResult();
          if(!sessions[task]){result[task]=empty(task,frame,'unavailable','model_not_loaded');continue;}
          let raw;
          try{
            const prepared=prepareFace(frame,region,task),quality=assessFaceQuality(frame,region,prepared,task);
            if(!quality.usable){prepared.data.fill(0);result[task]={...empty(task,frame,'unknown',quality.reason),quality};continue;}
            raw=await run(task,prepared);
            if(!current(opts,version))return staleResult();
            {const features=Array.from(tensorValues(raw,'label',7));result.expression={...base(task,frame,'ok','expression_scores_computed'),features,quality,labels:[...manifest.models.expression.labels],scores:softmax(features),scoreType:'softmax_model_score',establishesInternalEmotion:false};}
          }catch(error){result[task]=empty(task,frame,'unknown',error.code||'inference_failed');}
          finally{releaseOutputs(raw);}
        }
        return result;
      }catch(error){for(const task of TASKS)if(task==='detection'||flags[task])result[task]=empty(task,frame,'unknown',error.code||'inference_failed');return result;}
      finally{busy=false;const finish=finishActive;finishActive=null;activeDone=null;if(finish)finish();}
      function staleResult(){for(const task of TASKS)if(task==='detection'||flags[task])result[task]=empty(task,frame,'unknown','stale_frame');return result;}
    }
    function dispose(){
      if(disposal)return disposal;
      destroyed=true;lifecycle++;
      disposal=(async()=>{
        await Promise.allSettled(Object.values(pending));if(activeDone)await activeDone;
        const owned=Object.entries(sessions);for(const task of TASKS)delete sessions[task];
        const released=await Promise.allSettled(owned.map(async([,session])=>session.release()));
        released.forEach((result,i)=>{if(result.status==='rejected')states[owned[i][0]]={readiness:'error',executionProvider:null,error:'session_release_failed'};});
        if(released.some(result=>result.status==='rejected'))fail('session_release_failed','All session releases were attempted, but at least one failed.');
      })();return disposal;
    }
    return {load,getStatus,analyzeFrame,dispose};
  }
  return {createPretrainedBackend,loadVerifiedRuntime,createLocalAssetReader,verifyAsset,sha256,prepareDetection,prepareFace,assessFaceQuality,decodeYuNet,similarity,inverseAffine,softmax,STANDARD_POINTS:STANDARD_POINTS.map(p=>Object.freeze([...p])),LANDMARK_KINDS:Object.freeze([...LANDMARK_KINDS])};
});

/* Expression-only dedicated worker. No enrollment, storage, provider or pack import. */
(function(scope){
 'use strict';
 let backend=null,runtime=null,loading=false,running=false,base=null;
 const reply=(id,value)=>scope.postMessage({id,...value});
 scope.onmessage=async event=>{
  const m=event.data||{},id=m.id;
  if(!Number.isSafeInteger(id)||id<1)return;
  try{
   if(m.type==='load'){
    if(loading||backend)throw Error('models_already_loading_or_loaded');
    let assetReader=null;
    if(m.assetFiles){
     const specs=Object.values(NexusPretrainedAssets.runtime.files).concat(Object.values(NexusPretrainedAssets.models));
     if(!Array.isArray(m.assetFiles)||m.assetFiles.length!==specs.length)throw Error('incomplete_local_assets');const files=new Map();
     for(const item of m.assetFiles){const spec=specs.find(s=>s.path===item.path);if(!spec||files.has(item.path)||!item.file||item.file.size!==spec.bytes||typeof item.file.arrayBuffer!=='function')throw Error('invalid_local_asset');files.set(item.path,item.file);}
     assetReader=async path=>{const file=files.get(path);if(!file)throw Error('unlisted_asset');return new Uint8Array(await file.arrayBuffer());};
    }else{
     const url=new URL(m.baseUrl);if(!['http:','https:'].includes(url.protocol)||url.origin!==scope.location.origin||url.username||url.password)throw Error('same_origin_assets_required');base=url.href;
    }
    loading=true;
    try{
     runtime=await NexusPretrainedVision.loadVerifiedRuntime({baseUrl:base,assetReader,executionProvider:'wasm'});
     backend=NexusPretrainedVision.createPretrainedBackend(runtime);
     await backend.load({expression:true});
     reply(id,{ok:true,status:backend.getStatus()});
    }finally{loading=false;}
   }else if(m.type==='frame'){
    if(!backend||loading)throw Error('models_not_loaded');
    if(running)throw Error('busy');
    running=true;
    try{
     const result=await backend.analyzeFrame(m.frame,{expressionEnabled:true});
     const value=result.expression;
     // Only derived expression scores leave this worker, never images, landmarks or features.
     reply(id,{ok:true,result:{status:value.status,reason:value.reason,scores:value.scores,labels:value.labels,observedAt:m.frame.capturedAt,establishesInternalEmotion:false}});
    }finally{m.frame?.pixels?.fill?.(0);running=false;}
   }else throw Error('unsupported_expression_request');
  }catch(error){reply(id,{ok:false,error:error.code||error.message||'expression_worker_failed'});}
 };
})(globalThis);
