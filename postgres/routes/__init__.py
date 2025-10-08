from fastapi import APIRouter

from .empresa import router as empresa_router
from .usuario import router as usuario_router
from .conductor import router as conductor_router
from .dispositivogps import router as dispositivogps_router
from .vehiculo import router as vehiculo_router
from .ubicacion import router as ubicacion_router
from .tramo import router as tramo_router
from .estadoViaje import router as estadoViaje_router
from .ruta import router as ruta_router
from .trip import router as trip_router
from .posiciongps import router as posiciongps_router
from .resumentrip import router as resumentrip_router
from .rol import router as rol_router
from .permiso import router as permiso_router
from .rolpermiso import router as rolpermiso_router
from .usuariorol import router as usuariorol_router
from .rutatramo import router as rutatramo_router
from .triptramo import router as triptramo_router
from .tripconductores import router as tripconductores_router
from .vehiculoconductor import router as vehiculoconductor_router
from .paradasautorizadas import router as paradasautorizadas_router
from .rutaparada import router as rutaparada_router
from .tipodispositivogps import router as tipodispositivosgps_router
from .tipovehiculo import router as tipovehiculo_router
from .triplog import router as triplog_router

from .login import router as login_router
from .devicetrackgps import router as devicetrackgps_router

from .newpoint import router as newpoint_router

api_router = APIRouter(prefix="/api")

api_router.include_router(empresa_router)
api_router.include_router(usuario_router)
api_router.include_router(conductor_router)
api_router.include_router(dispositivogps_router)
api_router.include_router(vehiculo_router)
api_router.include_router(ubicacion_router)
api_router.include_router(tramo_router)
api_router.include_router(estadoViaje_router)
api_router.include_router(ruta_router)
api_router.include_router(trip_router)
api_router.include_router(posiciongps_router)
api_router.include_router(resumentrip_router)
api_router.include_router(rol_router)
api_router.include_router(permiso_router)
api_router.include_router(rolpermiso_router)
api_router.include_router(usuariorol_router)
api_router.include_router(rutatramo_router)
api_router.include_router(triptramo_router)
api_router.include_router(tripconductores_router)
api_router.include_router(vehiculoconductor_router)
api_router.include_router(paradasautorizadas_router)
api_router.include_router(rutaparada_router)
api_router.include_router(tipodispositivosgps_router)
api_router.include_router(tipovehiculo_router)
api_router.include_router(triplog_router)

api_router.include_router(login_router)
api_router.include_router(devicetrackgps_router)

api_router.include_router(newpoint_router)