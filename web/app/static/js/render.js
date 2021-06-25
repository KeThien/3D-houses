
// CREATE THE SCENE
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
const myCanvas = document.getElementById('myCanvas')

const renderer = new THREE.WebGLRenderer({
    canvas: myCanvas,
    antialias: true
});
renderer.setSize(window.innerWidth, window.innerHeight)

// CREATE CUBE
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshPhongMaterial( { color: 0x8844aa } );
const cube = new THREE.Mesh( geometry, material );
scene.add( cube );

// CAMERA
camera.position.z = 2;
const controls = new THREE.OrbitControls( camera, renderer.domElement );
controls.autoRotate = true

// LIGHTS
const color = 0xFFFFFF;
const intensity = 1;
const light = new THREE.DirectionalLight(color, intensity);
light.position.set(-1, 2, 4);
scene.add(light);
var amb_light = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(amb_light);

// ANIMATION LOOP
function animate() {
  if (resizeRendererToDisplaySize(renderer)) {
    const canvas = renderer.domElement;
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
  }
	requestAnimationFrame( animate );
  // cube.rotation.x += 0.01;
	// cube.rotation.y += 0.01;
  controls.update();
	renderer.render( scene, camera );
}
animate();

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