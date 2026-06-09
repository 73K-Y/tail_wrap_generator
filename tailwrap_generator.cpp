// ---------------------------------------------------------
// "name": "Tail Wrap Generator",
// "author": "© 2026 Tommy Raffaello Hodoroaba",
// "version" : (1, 0, 6),
// "blender" : (5, 0, 0),
// ---------------------------------------------------------
#include <iostream>
#include <vector>

// ---------------------------------------------------------
// 1. STRUTTURA VETTORE
// In JavaScript non esistono le `struct` come in C/C++, useresti una `class` 
// oppure un semplice oggetto letterale {x: 0, y: 0, z: 0}.
// Se usi Three.js, questa è l'equivalente esatto della classe `THREE.Vector3`.
// ---------------------------------------------------------
struct Vector3 {
    float x, y, z;

    // In JS scriveresti un metodo di classe: lerp(other, t) { ... }
    Vector3 lerp(const Vector3& other, float t) const {
        return {
            x + (other.x - x) * t,
            y + (other.y - y) * t,
            z + (other.z - z) * t
        };
    }

    // ATTENZIONE JS: JavaScript NON supporta l'"overload degli operatori". 
    // In C++ posso fare `v1 + v2`. In JS questo darebbe errore (o unirebbe due stringhe).
    // In JS saresti costretto a scrivere metodi espliciti, es: `v1.add(v2)` o `v1.multiplyScalar(5)`.
    Vector3 operator+(const Vector3& other) const { return { x + other.x, y + other.y, z + other.z }; }
    Vector3 operator*(float scalar) const { return { x * scalar, y * scalar, z * scalar }; }
};

// ---------------------------------------------------------
// 2. SETTINGS
// In C++ dichiaro una struttura rigida con tipi fissi (int, float).
// In JavaScript, questo sarebbe un normalissimo oggetto di configurazione (POJO):
// const settings = { lines: 8, segments: 10, thickness: 0.02, offset: 0.05 };
// Non devi dichiarare i tipi, JS è a tipizzazione dinamica (a meno che tu non usi TypeScript!).
// ---------------------------------------------------------
struct TailWrapSettings {
    int lines = 8;
    int segments = 10;
    float thickness = 0.02f;
    float offset = 0.05f;
};

// ---------------------------------------------------------
// 3. RAYCASTING / COLLISIONE
// In C++ passiamo i parametri per "riferimento" (outPoint, outNormal) usando la '&', 
// in modo che la funzione li modifichi direttamente in memoria.
// In JS i tipi primitivi (numeri) passano per valore. Per simulare questo in JS, 
// o restituisci un oggetto { point: p, normal: n, success: true }, 
// oppure passi oggetti Vector3 che vengono modificati internamente (es: raycaster.intersectObject in Three.js).
// ---------------------------------------------------------
bool getClosestPointOnMesh(const Vector3& point, Vector3& outPoint, Vector3& outNormal) {
    // Finta logica: in Three.js qui useresti un THREE.Raycaster o la libreria three-mesh-bvh 
    // sparando un raggio dal punto verso la mesh per trovare l'intersezione.
    outPoint = point;
    outNormal = { 0.0f, 0.0f, 1.0f };
    return true;
}

// ---------------------------------------------------------
// 4. L'ALGORITMO PRINCIPALE
// In C++ usiamo std::vector, che sono array dinamici rigidamente tipizzati.
// In JS useresti i normali Array `[]` che possono contenere qualsiasi cosa.
// NOTA PERFORMANCE WEB: se devi renderizzare in WebGL (Canvas), in JS è molto 
// meglio usare i "Typed Arrays" come `Float32Array` invece degli Array normali, 
// perché vanno dritti alla memoria della scheda video senza pesare sul Garbage Collector.
// ---------------------------------------------------------
void generateTailWrap(const std::vector<Vector3>& starts, const std::vector<Vector3>& ends, const TailWrapSettings& settings) {

    // In JS: if (!starts.length || !ends.length) { console.error("Errore"); return; }
    if (starts.empty() || ends.empty()) {
        std::cerr << "Errore: Mancano i punti di partenza o di fine." << std::endl;
        return;
    }

    for (int i = 0; i < settings.lines; i++) {
        // In JS la divisione tra interi produce già un decimale (float). 
        // In C++ dobbiamo forzare il cast (float)i, altrimenti 5/10 farebbe 0 e non 0.5.
        float t = (settings.lines > 1) ? (float)i / (settings.lines - 1) : 0.0f;

        // In JS useresti Math.floor() o parseInt() per troncare il numero.
        int idxStart = static_cast<int>(t * (starts.size() - 1));
        int idxEnd = static_cast<int>(t * (ends.size() - 1));

        Vector3 p1 = starts[idxStart];
        Vector3 p2 = ends[idxEnd];

        // In JS: const curvePoints = new Array(settings.segments);
        std::vector<Vector3> curvePoints(settings.segments);

        for (int s = 0; s < settings.segments; s++) {
            float segmentT = (float)s / (settings.segments - 1);

            Vector3 currentPoint = p1.lerp(p2, segmentT);

            Vector3 meshPoint, meshNormal;
            bool success = getClosestPointOnMesh(currentPoint, meshPoint, meshNormal);

            if (success) {
                // In C++ usiamo l'operatore + e * che abbiamo "overloadato" sopra.
                // In JS scriveresti: curvePoints[s] = meshPoint.clone().add(meshNormal.clone().multiplyScalar(settings.offset));
                // (I `clone()` in JS servono per evitare di modificare per sbaglio i vettori originali).
                curvePoints[s] = meshPoint + (meshNormal * settings.offset);
            }
            else {
                curvePoints[s] = currentPoint;
            }
        }

        // In JS: console.log(`Generata curva ${i} con ${curvePoints.length} punti.`);
        // In Three.js, qui prenderesti i tuoi `curvePoints`, creeresti una `THREE.CatmullRomCurve3`,
        // e genereresti un `THREE.TubeGeometry` per renderizzare il cilindro 3D nel browser.
        std::cout << "Generata curva " << i << " con " << curvePoints.size() << " punti.\n";
    }
}

int main() {
    TailWrapSettings config;
    config.lines = 5;
    config.segments = 10;

    // In JS l'equivalente di questa inizializzazione di array sarebbe:
    // const startCircle = [new THREE.Vector3(1,0,1), new THREE.Vector3(0,1,1), ...];
    std::vector<Vector3> startCircle = { {1,0,1}, {0,1,1}, {-1,0,1}, {0,-1,1} };
    std::vector<Vector3> endCircle = { {0.5,0,0}, {0,0.5,0}, {-0.5,0,0}, {0,-0.5,0} };

    generateTailWrap(startCircle, endCircle, config);

    return 0;
}