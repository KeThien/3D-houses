const myCanvas = document.getElementById("myCanvas");

const renderer = new THREE.WebGLRenderer({
  canvas: myCanvas,
  antialias: true,
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
// const cameraTarget = new THREE.Vector3( 0, - 0.1, 0 );

// CREATE THE SCENE
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x3241d19);
// scene.fog = new THREE.Fog( 0x72645b, 2, 15 );

// CAMERA
const fov = 35;
const canvas = renderer.domElement;
const aspect = canvas.clientWidth / canvas.clientHeight;
const near = 0.1;
const far = 1000;
const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
camera.position.x = 0;
camera.position.y = 0.9173680258001311;
camera.position.z = 1;

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.autoRotate = true;

// LIGHTS
function addShadowedLight(x, y, z, color, intensity) {
  var directionalLight = new THREE.DirectionalLight(color, intensity);
  directionalLight.position.set(x, y, z);
  scene.add(directionalLight);

  directionalLight.castShadow = true;

  var d = 1;
  directionalLight.shadow.camera.left = -d;
  directionalLight.shadow.camera.right = d;
  directionalLight.shadow.camera.top = d;
  directionalLight.shadow.camera.bottom = -d;

  directionalLight.shadow.camera.near = 1;
  directionalLight.shadow.camera.far = 4;

  directionalLight.shadow.mapSize.width = 1024;
  directionalLight.shadow.mapSize.height = 1024;

  directionalLight.shadow.bias = -0.001;
}
scene.add(new THREE.HemisphereLight(0x443333, 0x111122));
addShadowedLight(1, 1, 1, 0xffffff, 1.35);
addShadowedLight(0.5, 1, -1, 0xaaaabb, 1);

// AXESHELPER
// const axesHelper = new THREE.AxesHelper(5);
// scene.add(axesHelper);

// PLANE
const plane = new THREE.Mesh(
  new THREE.PlaneBufferGeometry(40, 40),
  new THREE.MeshStandardMaterial({ color: 0x1c1714, specular: 0x101010 })
);
plane.rotation.x = -Math.PI / 2;
plane.position.y = -0.5;
plane.receiveShadow = false;
// scene.add( plane );

// const base = "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/ply/"

// LOAD 3D MESH PLY
const loader = new THREE.PLYLoader();
function loadply(meshfile){
  loader.load(`./static/3d-models/${meshfile}`, function (geometry) {
    geometry.computeVertexNormals();
  
    // var material = new THREE.MeshStandardMaterial( { color: 0x0055ff, flatShading: true, vertexColors: true } );
    var material = new THREE.MeshStandardMaterial({
      flatShading: true,
      vertexColors: true,
      side: THREE.DoubleSide
    });
    var mesh = new THREE.Mesh(geometry, material);
  
    // mesh.position.x = 0;
    // mesh.position.y = 0;
    // mesh.position.z = 0;
    mesh.rotateOnAxis(new THREE.Vector3(1, 0, 0), -1.5708);
    // mesh.rotation.x = - Math.PI / 2;
    mesh.scale.multiplyScalar(0.01);
  
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    var position = {
      x: mesh.position.x,
      y: mesh.position.y,
      z: mesh.position.z,
    };
  
    //  CAMERA TARGET to object
    if (meshfile=='mesh0.ply'){
      controls.target = new THREE.Vector3(position);
      var bb = new THREE.Box3();
      bb.setFromObject(mesh);
      bb.getCenter(controls.target);
    }
  
    scene.add(mesh);
  });
}
let nmesh = localStorage.getItem('nmesh')
for (let i = 0; i < nmesh; i++){
    loadply(`mesh${i}.ply`);
}
// CREATE CUBE
// const geometry = new THREE.BoxGeometry();
// const material = new THREE.MeshPhongMaterial( { color: 0x8844aa } );
// const cube = new THREE.Mesh( geometry, material );
// scene.add( cube );

// ANIMATION LOOP
function rendering() {
  if (resizeRendererToDisplaySize(renderer)) {
    const canvas = renderer.domElement;
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
  }
  requestAnimationFrame(rendering);
  // cube.rotation.x += 0.01;
  // cube.rotation.y += 0.01;
  controls.update();
  // camera.position.x = Math.sin( timer ) * 2.5;
  // camera.position.z = Math.cos( timer ) * 2.5;

  // camera.lookAt( cameraTarget );

  renderer.render(scene, camera);
}
rendering();

// RESPONSIVE func
function resizeRendererToDisplaySize(renderer) {
  const canvas = renderer.domElement;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const needResize = canvas.width !== width || canvas.height !== height;
  if (needResize) {
    renderer.setSize(width, height, false);
  }
  return needResize;
}
