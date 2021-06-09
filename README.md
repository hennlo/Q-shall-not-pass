# Q shall not pass

This game was built as part of the lecture: Quantum Information at the University of Basel in the Spring Semester of 2021.

If you want to play this game please head to the download section and take a look at the short [tutorial page](tutorial.md)

## About
The purpose of the game is two fold.
For one I would like to give an example and teach others on a very basic level how quantum information works.
Secondly I want to use the nature and properties of qubits to implement several game mechanics using Quantum Computing.

For an in-depth explanation what the vision of this game is and how the specifc mechanics are implemented please read the full [project report]().

Although this games shall serve as an explanation on qubits, their states and how they behave when altered, this project does not teach you all the basics around quantum computing. It rather aims to visually show you how qubits can be "altered" and manipulated while discovering that the first impression of randomness isn't so random after all.

If you want to gain an in-depth view on quantum computing and the characteristics of qubits, please consult the [Qiskit Textbook](https://qiskit.org/textbook/preface.html) which already gives a perfect intorduction and overall explanation of the topic with great hands-on examples to try quantum computing for yourself.

The core of the repository is a fork from teh original [Qisge](https://github.com/TigrisCallidus/Qisge) repository.
Although most of it is used as is, there are a few altercations to the original work.Mainly to change input/output handling for the project-specific use case.
The main part od the project is still the **[game](Assets/StreamingAssets/Exchange/Data/game/game.py)**

## Start Playing

Simply download the most current release of the game [here](https://github.com/hennlo/Q-shall-not-pass/releases)
since we use Qisge to run and build the game you can simply follow the [installation](https://github.com/TigrisCallidus/Qisge#installation)

## How to use

If you want to make adaptations to the code and play around with the game and mechanics you can simply donwload the repository.
and add it to your Qisge

You can of course also look at the [game](Assets/StreamingAssets/Exchange/Data/game/game.py) itself, to get inspiration and see the magic behind everything.

## Game Mechanics

The game essentially revolves around three game mechanics, which
Use Quantum Computing.

1. A procedural level and map generation
2. Proportional character generation using the natural constraints of qubits and their expectation values
3. Matching player and gate proportions by comparing expectation values of player qubit and  passage qubit
4. Level progression: Forcing the user to execute a specific number of tasks in order to reach a certain level progress while internally applying rotation gates to achieve the desired target state


### Credits
This game was done with the help of:
*   **[Qisge](https://github.com/TigrisCallidus/Qisge)** a game engine enabling you to play pxthon games in [Unity](https://unity.com/).
Enabling you to use quantum computing inside your game.
* **[MicroQiskit](https://github.com/qiskit-community/MicroQiskit)** a simplified version of the feature-rich framework:  [Qiskit](https://qiskit.org/). This framework for quantum computing allows you to create quantum programs and run them either on advanced simulation devices or real prototype quantum devices.
* **[QuantumGraph](https://github.com/qiskit-community/QuantumGraph)** which helps to make quantum algorithms based on the manipulation of a tomography of a multi qubit device.
