DROP DATABASE IF EXISTS LaTradicional;
CREATE DATABASE LaTradicional;
USE LaTradicional;

-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: latradicional
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `idCliente` int NOT NULL AUTO_INCREMENT,
  `idPersona` int NOT NULL,
  `idUsuario` int NOT NULL,
  PRIMARY KEY (`idCliente`),
  KEY `idPersona` (`idPersona`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `cliente_ibfk_1` FOREIGN KEY (`idPersona`) REFERENCES `persona` (`idPersona`),
  CONSTRAINT `cliente_ibfk_2` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,4,4);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comprasrealizadas`
--

DROP TABLE IF EXISTS `comprasrealizadas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comprasrealizadas` (
  `id_comprasRealizadas` int NOT NULL AUTO_INCREMENT,
  `id_proveedor` int NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `fecha` date NOT NULL,
  `numeroOrden` varchar(50) NOT NULL,
  `estatus` int NOT NULL,
  PRIMARY KEY (`id_comprasRealizadas`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `comprasrealizadas_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comprasrealizadas`
--

LOCK TABLES `comprasrealizadas` WRITE;
/*!40000 ALTER TABLE `comprasrealizadas` DISABLE KEYS */;
/*!40000 ALTER TABLE `comprasrealizadas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `corte_caja`
--

DROP TABLE IF EXISTS `corte_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `corte_caja` (
  `id_ganancia` int NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `totalVenta` float NOT NULL,
  `cantidadCaja` decimal(10,2) NOT NULL,
  `diferencial` decimal(10,2) NOT NULL,
  `observaciones` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id_ganancia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `corte_caja`
--

LOCK TABLES `corte_caja` WRITE;
/*!40000 ALTER TABLE `corte_caja` DISABLE KEYS */;
/*!40000 ALTER TABLE `corte_caja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detallecompra`
--

DROP TABLE IF EXISTS `detallecompra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detallecompra` (
  `id_detalleCompra` int NOT NULL AUTO_INCREMENT,
  `descripcion` json NOT NULL,
  `compra_id` int NOT NULL,
  PRIMARY KEY (`id_detalleCompra`),
  KEY `compra_id` (`compra_id`),
  CONSTRAINT `detallecompra_ibfk_1` FOREIGN KEY (`compra_id`) REFERENCES `comprasrealizadas` (`id_comprasRealizadas`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detallecompra`
--

LOCK TABLES `detallecompra` WRITE;
/*!40000 ALTER TABLE `detallecompra` DISABLE KEYS */;
/*!40000 ALTER TABLE `detallecompra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalleventagalletas`
--

DROP TABLE IF EXISTS `detalleventagalletas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalleventagalletas` (
  `id_detalleVentaGalletas` int NOT NULL AUTO_INCREMENT,
  `venta_id` int NOT NULL,
  `lote_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_detalleVentaGalletas`),
  KEY `venta_id` (`venta_id`),
  KEY `lote_id` (`lote_id`),
  CONSTRAINT `detalleventagalletas_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id_venta`),
  CONSTRAINT `detalleventagalletas_ibfk_2` FOREIGN KEY (`lote_id`) REFERENCES `lotesgalletas` (`id_lote`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalleventagalletas`
--

LOCK TABLES `detalleventagalletas` WRITE;
/*!40000 ALTER TABLE `detalleventagalletas` DISABLE KEYS */;
INSERT INTO `detalleventagalletas` VALUES (11,13,1,2,10.00),(12,13,15,3,300.00),(13,13,3,3,300.00);
/*!40000 ALTER TABLE `detalleventagalletas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalleventaorden`
--

DROP TABLE IF EXISTS `detalleventaorden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalleventaorden` (
  `id_detalleVentaOrden` int NOT NULL AUTO_INCREMENT,
  `galletas_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `orden_id` int NOT NULL,
  PRIMARY KEY (`id_detalleVentaOrden`),
  KEY `galletas_id` (`galletas_id`),
  KEY `orden_id` (`orden_id`),
  CONSTRAINT `detalleventaorden_ibfk_1` FOREIGN KEY (`galletas_id`) REFERENCES `galletas` (`id_galleta`),
  CONSTRAINT `detalleventaorden_ibfk_2` FOREIGN KEY (`orden_id`) REFERENCES `orden` (`id_orden`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalleventaorden`
--

LOCK TABLES `detalleventaorden` WRITE;
/*!40000 ALTER TABLE `detalleventaorden` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalleventaorden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `idEmpleado` int NOT NULL AUTO_INCREMENT,
  `puesto` varchar(45) NOT NULL,
  `curp` varchar(18) NOT NULL,
  `rfc` varchar(13) NOT NULL,
  `salarioBruto` float NOT NULL,
  `fechaIngreso` date NOT NULL,
  `idPersona` int NOT NULL,
  `idUsuario` int NOT NULL,
  PRIMARY KEY (`idEmpleado`),
  KEY `idPersona` (`idPersona`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `empleado_ibfk_1` FOREIGN KEY (`idPersona`) REFERENCES `persona` (`idPersona`),
  CONSTRAINT `empleado_ibfk_2` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
INSERT INTO `empleado` VALUES (1,'Administrador','LOJA900101HDFPNSA1','LOJA900101ABC',25000,'2025-04-09',1,1),(2,'Producción','GOHU910202HDFPNSA2','GOHU910202ABC',15000,'2025-04-09',2,2),(3,'Cajero','PEJU920303HDFPNSA3','PEJU920303ABC',12000,'2025-04-09',3,3);
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `galletas`
--

DROP TABLE IF EXISTS `galletas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `galletas` (
  `id_galleta` int NOT NULL AUTO_INCREMENT,
  `tipo_galleta_id` int NOT NULL,
  `galleta` varchar(100) NOT NULL,
  `existencia` int NOT NULL,
  `receta_id` int NOT NULL,
  PRIMARY KEY (`id_galleta`),
  KEY `tipo_galleta_id` (`tipo_galleta_id`),
  KEY `receta_id` (`receta_id`),
  CONSTRAINT `galletas_ibfk_1` FOREIGN KEY (`tipo_galleta_id`) REFERENCES `tipo_galleta` (`id_tipo_galleta`),
  CONSTRAINT `galletas_ibfk_2` FOREIGN KEY (`receta_id`) REFERENCES `receta` (`idReceta`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `galletas`
--

LOCK TABLES `galletas` WRITE;
/*!40000 ALTER TABLE `galletas` DISABLE KEYS */;
INSERT INTO `galletas` VALUES (1,1,'Galleta de Nuez',123,1),(2,2,'Galleta de Nuez',24,1),(3,3,'Galleta de Nuez',38,1),(4,1,'Galleta de Chocolate',270,2),(5,2,'Galleta de Chocolate',33,2),(6,3,'Galleta de Chocolate',45,2),(7,1,'Galleta de Vainilla',225,3),(8,2,'Galleta de Vainilla',19,3),(9,3,'Galleta de Vainilla',33,3);
/*!40000 ALTER TABLE `galletas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos`
--

DROP TABLE IF EXISTS `insumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos` (
  `id_insumo` int NOT NULL AUTO_INCREMENT,
  `nombreInsumo` varchar(100) NOT NULL,
  `marca` varchar(30) NOT NULL,
  `unidad` varchar(50) NOT NULL,
  `total` float NOT NULL,
  `id_proveedor` int NOT NULL,
  PRIMARY KEY (`id_insumo`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `insumos_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos`
--

LOCK TABLES `insumos` WRITE;
/*!40000 ALTER TABLE `insumos` DISABLE KEYS */;
INSERT INTO `insumos` VALUES (1,'Harina','Harina R','Gramos',80000,1),(2,'Mantequilla','Mantequillin','Gramos',80500,1),(3,'Nuez','Nuez del mundo','Gramos',80700,1),(4,'Azúcar','Azúcar dulce','Gramos',80600,1),(5,'Huevo','La granja','Unidad',993,1),(6,'Chocolate en polvo','choco','Gramos',81000,1),(7,'Harina de trigo','Harina','Gramos',81000,1),(8,'Mantequilla sin sal','mante','Gramos',81000,1),(9,'Azúcar morena','azucar','Gramos',81000,1),(10,'Esencia de vainilla','vainilla','Mililitros',81000,1),(11,'Polvo para hornear','polvo','Gramos',81000,1);
/*!40000 ALTER TABLE `insumos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loteinsumo`
--

DROP TABLE IF EXISTS `loteinsumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loteinsumo` (
  `idLote` int NOT NULL AUTO_INCREMENT,
  `id_insumo` int NOT NULL,
  `fechaIngreso` date NOT NULL,
  `fechaCaducidad` date NOT NULL,
  `cantidad` int NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  PRIMARY KEY (`idLote`),
  KEY `id_insumo` (`id_insumo`),
  CONSTRAINT `loteinsumo_ibfk_1` FOREIGN KEY (`id_insumo`) REFERENCES `insumos` (`id_insumo`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loteinsumo`
--

LOCK TABLES `loteinsumo` WRITE;
/*!40000 ALTER TABLE `loteinsumo` DISABLE KEYS */;
INSERT INTO `loteinsumo` VALUES (1,4,'2025-04-07','2025-04-11',80600,9.00),(2,1,'2025-04-07','2025-04-25',80000,9.00),(3,5,'2025-04-07','2025-04-19',993,9.00),(4,2,'2025-04-07','2025-05-03',80500,9.00),(5,3,'2025-04-07','2025-05-03',80700,9.00),(6,6,'2025-04-08','2025-04-18',81000,9.00),(7,7,'2025-04-08','2025-04-19',81000,9.00),(8,8,'2025-04-08','2025-05-10',81000,9.00),(9,9,'2025-04-08','2025-04-19',81000,9.00),(10,10,'2025-04-08','2025-04-18',81000,9.00),(11,11,'2025-04-08','2025-05-03',81000,9.00);
/*!40000 ALTER TABLE `loteinsumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lotesgalletas`
--

DROP TABLE IF EXISTS `lotesgalletas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lotesgalletas` (
  `id_lote` int NOT NULL AUTO_INCREMENT,
  `galleta_id` int NOT NULL,
  `fechaProduccion` date NOT NULL,
  `fechaCaducidad` date NOT NULL,
  `cantidad` int NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  `existencia` int NOT NULL,
  PRIMARY KEY (`id_lote`),
  KEY `galleta_id` (`galleta_id`),
  CONSTRAINT `lotesgalletas_ibfk_1` FOREIGN KEY (`galleta_id`) REFERENCES `galletas` (`id_galleta`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lotesgalletas`
--

LOCK TABLES `lotesgalletas` WRITE;
/*!40000 ALTER TABLE `lotesgalletas` DISABLE KEYS */;
INSERT INTO `lotesgalletas` VALUES (1,1,'2023-10-01','2025-05-01',100,250.00,78),(2,1,'2023-10-05','2025-05-03',50,300.00,45),(3,2,'2023-10-05','2025-05-05',15,1200.00,9),(4,2,'2023-10-08','2025-05-07',20,1600.00,15),(5,3,'2023-10-10','2025-05-09',20,840.00,18),(6,3,'2023-10-12','2025-05-11',25,1050.00,20),(7,4,'2023-10-02','2025-05-02',150,300.00,120),(8,4,'2023-10-06','2025-05-04',160,320.00,150),(9,5,'2023-10-06','2025-05-06',18,1500.00,15),(10,5,'2023-10-09','2025-05-08',20,1700.00,18),(11,6,'2023-10-11','2025-05-10',25,1050.00,20),(12,6,'2023-10-13','2025-05-12',30,1260.00,25),(13,7,'2023-10-03','2025-05-13',125,275.00,100),(14,7,'2023-10-07','2025-05-15',140,308.00,125),(15,8,'2023-10-07','2025-05-14',12,1300.00,7),(16,8,'2023-10-10','2025-05-16',15,1625.00,12),(17,9,'2023-10-12','2025-05-17',18,945.00,15),(18,9,'2023-10-14','2025-05-18',20,1050.00,18);
/*!40000 ALTER TABLE `lotesgalletas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mermasgalletas`
--

DROP TABLE IF EXISTS `mermasgalletas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mermasgalletas` (
  `id_merma` int NOT NULL AUTO_INCREMENT,
  `lote_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `tipo_merma` varchar(50) NOT NULL,
  `fecha` date NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id_merma`),
  KEY `lote_id` (`lote_id`),
  CONSTRAINT `mermasgalletas_ibfk_1` FOREIGN KEY (`lote_id`) REFERENCES `lotesgalletas` (`id_lote`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mermasgalletas`
--

LOCK TABLES `mermasgalletas` WRITE;
/*!40000 ALTER TABLE `mermasgalletas` DISABLE KEYS */;
/*!40000 ALTER TABLE `mermasgalletas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mermasinsumos`
--

DROP TABLE IF EXISTS `mermasinsumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mermasinsumos` (
  `id_merma` int NOT NULL AUTO_INCREMENT,
  `lote_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `tipo_merma` varchar(50) NOT NULL,
  `descripcion` text,
  `fecha` date NOT NULL,
  PRIMARY KEY (`id_merma`),
  KEY `lote_id` (`lote_id`),
  CONSTRAINT `mermasinsumos_ibfk_1` FOREIGN KEY (`lote_id`) REFERENCES `loteinsumo` (`idLote`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mermasinsumos`
--

LOCK TABLES `mermasinsumos` WRITE;
/*!40000 ALTER TABLE `mermasinsumos` DISABLE KEYS */;
/*!40000 ALTER TABLE `mermasinsumos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orden`
--

DROP TABLE IF EXISTS `orden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden` (
  `id_orden` int NOT NULL AUTO_INCREMENT,
  `descripcion` text,
  `total` decimal(10,2) NOT NULL,
  `fechaAlta` datetime NOT NULL,
  `fechaEntrega` datetime NOT NULL,
  `tipoVenta` varchar(50) NOT NULL,
  `cliente_id` int NOT NULL,
  PRIMARY KEY (`id_orden`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `orden_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`idCliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden`
--

LOCK TABLES `orden` WRITE;
/*!40000 ALTER TABLE `orden` DISABLE KEYS */;
/*!40000 ALTER TABLE `orden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `persona`
--

DROP TABLE IF EXISTS `persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona` (
  `idPersona` int NOT NULL AUTO_INCREMENT,
  `genero` varchar(1) NOT NULL,
  `apPaterno` varchar(20) NOT NULL,
  `apMaterno` varchar(20) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `telefono` varchar(10) NOT NULL,
  `calle` varchar(50) NOT NULL,
  `numero` int NOT NULL,
  `colonia` varchar(50) NOT NULL,
  `codigoPostal` int NOT NULL,
  `email` varchar(100) NOT NULL,
  `fechaNacimiento` date NOT NULL,
  PRIMARY KEY (`idPersona`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona`
--

LOCK TABLES `persona` WRITE;
/*!40000 ALTER TABLE `persona` DISABLE KEYS */;
INSERT INTO `persona` VALUES (1,'M','Lopez','Jose','Jose','1234567890','Calle Admin',1,'Colonia Admin',12345,'admin@example.com','1990-01-01'),(2,'M','Gonzales','Martinez','Hugo','2345678901','Calle Prod',2,'Colonia Prod',23456,'prod@example.com','1991-02-02'),(3,'M','Perez','Morales','Juan','3456789012','Calle Cajero',3,'Colonia Cajero',34567,'cajero@example.com','1992-03-03'),(4,'H','Landin','Lopez','Diego','4775189860','Cerro del Gigante',1014,'Real de Jerez',37538,'inventateuno0@gmail.com','2025-04-09');
/*!40000 ALTER TABLE `persona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `id_proveedor` int NOT NULL AUTO_INCREMENT,
  `empresa` varchar(100) NOT NULL,
  `fechaRegistro` date NOT NULL,
  `estatus` int NOT NULL,
  `calle` varchar(50) NOT NULL,
  `numero` int NOT NULL,
  `colonia` varchar(50) NOT NULL,
  `codigoPostal` int NOT NULL,
  `telefono` varchar(10) NOT NULL,
  `email` varchar(100) NOT NULL,
  `rfc` varchar(12) NOT NULL,
  PRIMARY KEY (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
INSERT INTO `proveedor` VALUES (1,'Harinas Finas S.A.','2020-05-15',1,'Av. Industrial',1250,'Zona Industrial',54090,'5512345678','ventas@harinasfinas.com','HFI120515ABC'),(2,'Azúcar Dulce México','2019-11-22',1,'Calle Dulcería',340,'Centro',55010,'5556781234','contacto@azucardulce.mx','ADM191122XYZ'),(3,'Huevos Frescos del Valle','2021-03-10',1,'Camino Rural',45,'San Juan',54330,'5543218765','pedidos@huevosfrescos.com','HFV210310MNO'),(4,'Mantequillas Golden','2020-08-05',1,'Blvd. Lácteos',780,'Lomas Blancas',54120,'5578901234','info@goldenbutter.com','MGL200805PQR'),(5,'Especias Tradicionales','2018-07-30',1,'Callejón Especias',12,'Mercado de Abastos',54050,'5512456789','especias@tradicional.com','ETR180730JKL'),(6,'Frutas Secas Selectas','2021-01-18',1,'Av. Frutal',560,'Parque Industrial',54200,'5587654321','ventas@frutassecas.com','FSS210118DEF'),(7,'Chocolate Premium','2019-09-14',1,'Calle Cacao',220,'Zona Cobertura',54340,'5532145698','choco@premium.mx','CPM190914GHI'),(8,'Levaduras Naturales','2020-02-28',1,'Prol. Fermentación',150,'Polanco',54150,'5598765432','levaduras@naturales.com','LNV200228STU'),(9,'Vainilla Pura de Papantla','2018-12-05',1,'Camino Vainilla',80,'Papantla Centro',54180,'5545678912','purevainilla@papantla.com','VPP181205VWX'),(10,'Embalajes para Panadería','2021-06-20',1,'Av. del Empaque',320,'Parque Logístico',54250,'5578912345','embalajes@panaderia.com','EPP210620YZA');
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receta`
--

DROP TABLE IF EXISTS `receta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta` (
  `idReceta` int NOT NULL AUTO_INCREMENT,
  `nombreReceta` varchar(50) NOT NULL,
  `ingredientes` json NOT NULL,
  `Descripccion` text,
  `estatus` int DEFAULT NULL,
  `cantidad_galletas` int NOT NULL,
  `imagen_galleta` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`idReceta`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receta`
--

LOCK TABLES `receta` WRITE;
/*!40000 ALTER TABLE `receta` DISABLE KEYS */;
INSERT INTO `receta` VALUES (1,'Galleta de Nuez','[{\"insumo\": \"Harina\", \"unidad\": \"Gramos\", \"cantidad\": \"500\"}, {\"insumo\": \"Mantequilla\", \"unidad\": \"Gramos\", \"cantidad\": \"250\"}, {\"insumo\": \"Nuez\", \"unidad\": \"Gramos\", \"cantidad\": \"150\"}, {\"insumo\": \"Azúcar\", \"unidad\": \"Gramos\", \"cantidad\": \"200\"}, {\"insumo\": \"Huevo\", \"unidad\": \"Unidad\", \"cantidad\": \"3\"}]','1. Mezclar la mantequilla ablandada con el azúcar hasta cremar. \n   2. Añadir los huevos uno a uno, mezclando bien después de cada adición.\n   3. Incorporar la harina poco a poco hasta formar una masa homogénea.\n   4. Agregar las nueces picadas y mezclar uniformemente.\n   5. Formar bolitas y aplanarlas ligeramente sobre una bandeja para horno.\n   6. Hornear a 180°C durante 12-15 minutos hasta dorar.',1,100,NULL),(2,'Galleta de Chocolate','[{\"insumo\": \"Harina\", \"unidad\": \"Gramos\", \"cantidad\": \"450\"}, {\"insumo\": \"Mantequilla\", \"unidad\": \"Gramos\", \"cantidad\": \"200\"}, {\"insumo\": \"Chocolate en polvo\", \"unidad\": \"Gramos\", \"cantidad\": \"120\"}, {\"insumo\": \"Azúcar\", \"unidad\": \"Gramos\", \"cantidad\": \"180\"}, {\"insumo\": \"Huevo\", \"unidad\": \"Unidad\", \"cantidad\": \"4\"}]','1. Batir la mantequilla con el azúcar hasta obtener una mezcla esponjosa.\n   2. Añadir los huevos y mezclar bien.\n   3. Incorporar el chocolate en polvo y mezclar.\n   4. Agregar la harina poco a poco hasta formar una masa consistente.\n   5. Dejar reposar la masa 30 minutos en refrigeración.\n   6. Formar galletas y hornear a 170°C durante 10-12 minutos.',1,200,NULL),(3,'Galleta de Vainilla','[{\"insumo\": \"Harina de trigo\", \"unidad\": \"Gramos\", \"cantidad\": \"500\"}, {\"insumo\": \"Mantequilla sin sal\", \"unidad\": \"Gramos\", \"cantidad\": \"250\"}, {\"insumo\": \"Azúcar morena\", \"unidad\": \"Gramos\", \"cantidad\": \"200\"}, {\"insumo\": \"Nueces picadas\", \"unidad\": \"Gramos\", \"cantidad\": \"150\"}, {\"insumo\": \"Esencia de vainilla\", \"unidad\": \"Mililitros\", \"cantidad\": \"10\"}, {\"insumo\": \"Huevo\", \"unidad\": \"Unidad\", \"cantidad\": \"2\"}, {\"insumo\": \"Polvo para hornear\", \"unidad\": \"Gramos\", \"cantidad\": \"5\"}]','1. Batir la mantequilla con el azúcar morena hasta cremar.\n   2. Añadir los huevos y la esencia de vainilla, mezclar bien.\n   3. Incorporar la harina previamente mezclada con el polvo para hornear.\n   4. Agregar las nueces picadas y mezclar uniformemente.\n   5. Refrigerar la masa por 1 hora para que sea más manejable.\n   6. Formar galletas y hornear a 175°C durante 15 minutos o hasta dorar ligeramente.',1,120,NULL);
/*!40000 ALTER TABLE `receta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudproduccion`
--

DROP TABLE IF EXISTS `solicitudproduccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudproduccion` (
  `idSolicitud` int NOT NULL AUTO_INCREMENT,
  `detalleorden_id` int NOT NULL,
  `fechaCaducidad` date NOT NULL,
  `estatus` int NOT NULL,
  PRIMARY KEY (`idSolicitud`),
  KEY `detalleorden_id` (`detalleorden_id`),
  CONSTRAINT `solicitudproduccion_ibfk_1` FOREIGN KEY (`detalleorden_id`) REFERENCES `detalleventaorden` (`id_detalleVentaOrden`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudproduccion`
--

LOCK TABLES `solicitudproduccion` WRITE;
/*!40000 ALTER TABLE `solicitudproduccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `solicitudproduccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_galleta`
--

DROP TABLE IF EXISTS `tipo_galleta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_galleta` (
  `id_tipo_galleta` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_tipo_galleta`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_galleta`
--

LOCK TABLES `tipo_galleta` WRITE;
/*!40000 ALTER TABLE `tipo_galleta` DISABLE KEYS */;
INSERT INTO `tipo_galleta` VALUES (1,'Unidad',5.00),(2,'Caja de Kilo',100.00),(3,'Caja de 700 Gramos',70.00);
/*!40000 ALTER TABLE `tipo_galleta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `idUsuario` int NOT NULL AUTO_INCREMENT,
  `nombreUsuario` varchar(20) NOT NULL,
  `token` varchar(255) DEFAULT NULL,
  `estatus` int NOT NULL,
  `contrasenia` text NOT NULL,
  `rol` varchar(4) NOT NULL,
  `ultima_conexion` datetime DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  UNIQUE KEY `nombreUsuario` (`nombreUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'LopezJose',NULL,1,'scrypt:32768:8:1$ZwjzhaY9VlDJPEf8$4fb6058753364581ddcf81dbf7058fb2a8f1fafaed093709e59d1a9247d71fe2b5d5d5eef80f46102b601a47a6d063d589ab64b1697a4f91e147c2b7419d031f','ADMS','2025-04-09 21:59:14'),(2,'GonzalesHugo',NULL,1,'scrypt:32768:8:1$VD0RYrPIUGRm1KAH$2f0a3217f3d706e45e043897e16d66c0bd1e6f5d7a6462bcf34341a2335fd4d084fe49d2d9357d6d94e920020c539a9c1cc651e8d4571539e51a6a2c4be643d7','PROD',NULL),(3,'PerezJuan',NULL,1,'scrypt:32768:8:1$tcQt5gt7KkQRfaJG$015da336bf397e1a1eab6e61ea8b4f36aca896cfa5b4e92c264ef9bfc4f0e3810ddf891ab391a68d2e786aa05454a89ec127a73cb969b59ae94bc008761a1ea5','CAJA',NULL),(4,'landindiego',NULL,1,'scrypt:32768:8:1$btOlyJ9dwwcC2t46$461a2b4883548271f308a410871e3c9467e9722a59d51e7953739b77f0dcbfc8ee36e87ab4829ffa30b760e2f0c9ec251c8a70284a27492e6501f83a02fd5ae8','CLIE','2025-04-09 21:58:16');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_seguridad`
--

DROP TABLE IF EXISTS `usuario_seguridad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_seguridad` (
  `idUsuarioSeguridad` int NOT NULL AUTO_INCREMENT,
  `idUsuario` int NOT NULL,
  `failed_login_attempts` int NOT NULL,
  `password_last_changed` datetime NOT NULL,
  PRIMARY KEY (`idUsuarioSeguridad`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `usuario_seguridad_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_seguridad`
--

LOCK TABLES `usuario_seguridad` WRITE;
/*!40000 ALTER TABLE `usuario_seguridad` DISABLE KEYS */;
INSERT INTO `usuario_seguridad` VALUES (1,4,0,'2025-04-09 21:57:26'),(2,1,0,'2025-04-09 21:59:14');
/*!40000 ALTER TABLE `usuario_seguridad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id_venta` int NOT NULL AUTO_INCREMENT,
  `total` decimal(10,2) NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `ticket` text,
  `tipoVenta` varchar(50) NOT NULL,
  PRIMARY KEY (`id_venta`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (8,200.00,'2025-04-03','10:30:00','TICKET-001-2023','Punto de Venta'),(9,480.00,'2025-04-04','12:45:00','TICKET-002-2023','Portal Cliente'),(10,220.00,'2025-04-05','09:15:00','TICKET-003-2023','Punto de Venta'),(11,590.00,'2025-04-06','14:20:00','TICKET-004-2023','Portal Cliente'),(12,315.00,'2025-04-07','11:00:00','TICKET-005-2023','Punto de Venta'),(13,610.00,'2025-04-09','22:00:58','TK-20250409220057','Punto de Venta');
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `verificacion_usuario`
--

DROP TABLE IF EXISTS `verificacion_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `verificacion_usuario` (
  `idVerificacion` int NOT NULL AUTO_INCREMENT,
  `idUsuario` int NOT NULL,
  `verificado` tinyint(1) NOT NULL,
  `codigo_verificacion` varchar(32) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`idVerificacion`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `verificacion_usuario_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `verificacion_usuario`
--

LOCK TABLES `verificacion_usuario` WRITE;
/*!40000 ALTER TABLE `verificacion_usuario` DISABLE KEYS */;
INSERT INTO `verificacion_usuario` VALUES (1,4,1,NULL,'2025-04-09 21:57:26');
/*!40000 ALTER TABLE `verificacion_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'latradicional'
--

--
-- Dumping routines for database 'latradicional'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-09 22:08:29

SELECT * FROM cliente;
SELECT * FROM comprasrealizadas;
SELECT * FROM corte_caja;
SELECT * FROM detallecompra;
SELECT * FROM detalleventagalletas;
SELECT * FROM detalleventaorden;
SELECT * FROM empleado;
SELECT * FROM galletas;
SELECT * FROM insumos;
SELECT * FROM loteinsumo;
SELECT * FROM lotesgalletas;
SELECT * FROM mermasgalletas;
SELECT * FROM mermasinsumos;
SELECT * FROM orden;
SELECT * FROM persona;
SELECT * FROM proveedor;
SELECT * FROM receta;
SELECT * FROM solicitudproduccion;
SELECT * FROM tipo_galleta;
SELECT * FROM usuario;
SELECT * FROM usuario_seguridad;
SELECT * FROM ventas;
SELECT * FROM verificacion_usuario;
