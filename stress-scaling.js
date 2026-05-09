import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Calentamiento
    { duration: '1m', target: 100 },  // Inyección de estrés 
    { duration: '2m', target: 100 },  // Mantenimiento para forzar al HPA
    { duration: '30s', target: 0 },   // Enfriamiento
  ],
  // Es buena práctica definir umbrales para saber si la latencia p95 se dispara
  thresholds: {
    http_req_duration: ['p(95)<500'], // Queremos monitorear el p95, como indica tu tesis
  },
};

export default function () {
  // Asegúrate de apuntar al Ingress o al servicio expuesto de Google Online Boutique
  const res = http.get('http://localhost:80'); 
  
  // Validamos que el microservicio esté respondiendo correctamente (código 200)
  check(res, {
    'status es 200': (r) => r.status === 200,
  });
  
  sleep(1);
}