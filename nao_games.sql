-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le : lun. 28 avr. 2025 à 16:15
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `nao_games`
--

-- --------------------------------------------------------

--
-- Structure de la table `faces`
--

CREATE TABLE `faces` (
  `id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `face_data` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `ListeQuestions`
--

CREATE TABLE `ListeQuestions` (
  `id` int(11) NOT NULL,
  `question` varchar(1000) DEFAULT NULL,
  `reponse` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `ListeQuestions`
--

INSERT INTO `ListeQuestions` (`id`, `question`, `reponse`) VALUES
(1, 'Question, je suis un mammifère marin, intelligent et qui aiment sauter hors de l\'eau. Je me trouve assez souvent à Tamarin. Qui suis je ?', 'dauphin'),
(2, 'Question, Je suis un gigantesque mammifère marin et je peux être aussi long que les bus de port louis. Je me trouve assez souvent à Tamarin. Qui suis je ?', 'baleine'),
(3, 'Question, j\'ai une grosse carapace dur sur le dos pour me protéger dans l\'océan. Je suis de couleur verte et mes pattes ressemblent à des nageoires de poisson. Je vis généralement à îles aux cerfs. Qui suis je ?', 'tortue de mer'),
(4, 'Question, Je suis un prédateur qui ressemble à un serpent. J\'aime me cacher en dessous des rochers mais j\'en sors seulement pour chasser des poissons. Je vis généralement soit à Tamarin soit à Blue Bay. Qui suis je ?', 'murène'),
(5, 'Question, Je suis un poisson coloré qui ressemble un peu à un perroquet à cause de ma bouche en forme de bec. Je me trouve auprès des récifs coraliens de flic en flac et îles aux cerfs. Qui suis je ?', 'poisson-perroquet'),
(6, 'Question, Je suis un petit poisson coloré à rayures blanches qui aime bien me cacher dans des anémones de mer. Je suis souvent comparé à Nemo. Je vis aux alentours des coraux de Blue bay Qui suis je ?', 'poisson-clown'),
(7, 'Question, J\'ai une carapace tout le long de mon corps, j\'ai des pinces qui me servent à attraper ma nourriture et me défendre. Je vis généralement dans un trou sur une plage. Qui suis je ?', 'crabe'),
(8, 'Question, Je suis un poisson marin avec un corps plat, en forme d\'aile. J\'aime me poser sur le sable au fond de l\'eau. Je vis particulièrement au sud de l\'île entre Le morne et Bel Ombre. Qui suis je ?', 'raie'),
(9, 'Question, Je suis un animal intelligent avec un corps mou et une tête ronde. J\'ai huit bras longs qui ressemblent à des tentacules. Je peux aussi changer de couleur pour me camoufler des prédateurs. Je vis un peu partout autour de l\'île. Qui suis je ?', 'pieuvre'),
(10, 'Question, Je suis un prédateur avec une nageoire sur mon dos qui fait peur. Je possède une rangée de dents pointues. Mais pas d\'inquiétude, je ne suis pas très souvent présent à Maurice. Qui suis je ?', 'requin');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `faces`
--
ALTER TABLE `faces`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `ListeQuestions`
--
ALTER TABLE `ListeQuestions`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `faces`
--
ALTER TABLE `faces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT pour la table `ListeQuestions`
--
ALTER TABLE `ListeQuestions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
