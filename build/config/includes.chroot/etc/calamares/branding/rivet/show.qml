import QtQuick 2.5
import calamares.slideshow 1.0

Presentation {
    id: presentation

    // The installer slideshow is a game surface, not a navigable presentation.
    // Keep clicks and navigation keys from accidentally switching slides.
    mouseNavigation: false
    arrowNavigation: false
    keyShortcutsEnabled: false

    Slide {
        id: gameSlide
        title: qsTr("Installing Rivet Linux")
        notes: qsTr("Rivet Pong: move the mouse to control the left paddle. The first to reach five points wins.")

        Rectangle {
            id: rivetPongField
            anchors.fill: parent
            color: "#0b1720"
            radius: 12
            border.color: "#20c997"
            border.width: 2

            property int targetScore: 5
            property int playerScore: 0
            property int computerScore: 0
            property bool gameStarted: false
            property bool gameFinished: false
            property real ballVelocityX: 0
            property real ballVelocityY: 0

            function resetGame() {
                playerScore = 0
                computerScore = 0
                gameStarted = false
                gameFinished = false
                ballVelocityX = 0
                ballVelocityY = 0
                playerPaddle.y = (court.height - playerPaddle.height) / 2
                computerPaddle.y = (court.height - computerPaddle.height) / 2
                ball.x = (court.width - ball.width) / 2
                ball.y = (court.height - ball.height) / 2
            }

            function serve(direction) {
                ball.x = (court.width - ball.width) / 2
                ball.y = (court.height - ball.height) / 2
                ballVelocityX = court.width * 0.0055 * direction
                ballVelocityY = court.height * (Math.random() * 0.008 - 0.004)

                if (Math.abs(ballVelocityY) < court.height * 0.0018) {
                    ballVelocityY = court.height * 0.0018 * (Math.random() < 0.5 ? -1 : 1)
                }

                gameFinished = false
                gameStarted = true
            }

            function finishGame() {
                gameStarted = false
                gameFinished = true
                ballVelocityX = 0
                ballVelocityY = 0
            }

            function awardPlayerPoint() {
                playerScore += 1
                if (playerScore >= targetScore) {
                    finishGame()
                } else {
                    serve(1)
                }
            }

            function awardComputerPoint() {
                computerScore += 1
                if (computerScore >= targetScore) {
                    finishGame()
                } else {
                    serve(-1)
                }
            }

            function advanceGame() {
                if (!gameStarted || gameFinished || court.width <= 0 || court.height <= 0) {
                    return
                }

                // The computer tracks the ball, but deliberately leaves room to beat it.
                var targetY
                if (ballVelocityX > 0) {
                    targetY = ball.y + ball.height / 2 - computerPaddle.height / 2
                } else {
                    targetY = (court.height - computerPaddle.height) / 2
                }
                var tracking = ballVelocityX > 0 ? 0.065 : 0.035
                computerPaddle.y += (targetY - computerPaddle.y) * tracking
                computerPaddle.y = Math.max(0, Math.min(court.height - computerPaddle.height, computerPaddle.y))

                ball.x += ballVelocityX
                ball.y += ballVelocityY

                if (ball.y < 0) {
                    ball.y = 0
                    ballVelocityY = Math.abs(ballVelocityY)
                } else if (ball.y + ball.height > court.height) {
                    ball.y = court.height - ball.height
                    ballVelocityY = -Math.abs(ballVelocityY)
                }

                if (ballVelocityX < 0
                        && ball.x <= playerPaddle.x + playerPaddle.width
                        && ball.x + ball.width >= playerPaddle.x
                        && ball.y + ball.height >= playerPaddle.y
                        && ball.y <= playerPaddle.y + playerPaddle.height) {
                    var playerImpact = (ball.y + ball.height / 2
                                        - (playerPaddle.y + playerPaddle.height / 2))
                                       / (playerPaddle.height / 2)
                    ballVelocityX = Math.min(Math.abs(ballVelocityX) * 1.04, court.width * 0.012)
                    ballVelocityY = Math.max(-court.height * 0.012,
                                              Math.min(court.height * 0.012,
                                                       playerImpact * court.height * 0.008))
                    ball.x = playerPaddle.x + playerPaddle.width + 2
                }

                if (ballVelocityX > 0
                        && ball.x + ball.width >= computerPaddle.x
                        && ball.x <= computerPaddle.x + computerPaddle.width
                        && ball.y + ball.height >= computerPaddle.y
                        && ball.y <= computerPaddle.y + computerPaddle.height) {
                    var computerImpact = (ball.y + ball.height / 2
                                          - (computerPaddle.y + computerPaddle.height / 2))
                                         / (computerPaddle.height / 2)
                    ballVelocityX = -Math.min(Math.abs(ballVelocityX) * 1.04, court.width * 0.012)
                    ballVelocityY = Math.max(-court.height * 0.012,
                                              Math.min(court.height * 0.012,
                                                       computerImpact * court.height * 0.008))
                    ball.x = computerPaddle.x - ball.width - 2
                }

                if (ball.x + ball.width < 0) {
                    awardComputerPoint()
                } else if (ball.x > court.width) {
                    awardPlayerPoint()
                }
            }

            Text {
                id: gameTitle
                x: 14
                y: 9
                text: "RIVET PONG"
                color: "#e9fff8"
                font.bold: true
                font.pixelSize: Math.max(16, rivetPongField.height * 0.055)
            }

            Text {
                id: scoreText
                anchors.horizontalCenter: parent.horizontalCenter
                y: 9
                text: rivetPongField.playerScore + "  :  " + rivetPongField.computerScore
                color: "#e9fff8"
                font.bold: true
                font.pixelSize: Math.max(18, rivetPongField.height * 0.06)
            }

            Text {
                id: targetText
                anchors.right: parent.right
                anchors.rightMargin: 14
                y: 13
                text: qsTr("FIRST TO %1").arg(rivetPongField.targetScore)
                color: "#a9c5d0"
                font.pixelSize: Math.max(10, rivetPongField.height * 0.032)
            }

            Item {
                id: court
                x: 12
                y: 46
                width: parent.width - 24
                height: Math.max(80, parent.height - 58)
                clip: true

                Rectangle {
                    anchors.fill: parent
                    color: "#08121a"
                    radius: 7
                    border.color: "#24404b"
                    border.width: 1
                }

                Repeater {
                    model: 10
                    Rectangle {
                        x: (court.width - width) / 2
                        y: index * court.height / 10
                        width: 2
                        height: court.height / 18
                        radius: 1
                        color: "#49717d"
                        opacity: 0.75
                    }
                }

                Rectangle {
                    id: playerPaddle
                    x: court.width * 0.035
                    y: (court.height - height) / 2
                    width: Math.max(6, court.width * 0.022)
                    height: Math.max(34, court.height * 0.23)
                    radius: width / 2
                    color: "#20c997"
                }

                Rectangle {
                    id: computerPaddle
                    x: court.width - width - court.width * 0.035
                    y: (court.height - height) / 2
                    width: Math.max(6, court.width * 0.022)
                    height: Math.max(34, court.height * 0.23)
                    radius: width / 2
                    color: "#60a5fa"
                }

                Rectangle {
                    id: ball
                    width: Math.max(8, court.width * 0.022)
                    height: width
                    radius: width / 2
                    x: (court.width - width) / 2
                    y: (court.height - height) / 2
                    color: "#f2fff9"
                }

                Rectangle {
                    id: gameOverlay
                    anchors.fill: parent
                    z: 10
                    radius: 7
                    color: "#061018"
                    opacity: 0.91
                    visible: !rivetPongField.gameStarted

                    Text {
                        anchors.centerIn: parent
                        width: parent.width * 0.86
                        text: rivetPongField.gameFinished
                              ? (rivetPongField.playerScore >= rivetPongField.targetScore
                                 ? qsTr("YOU WIN!\nClick to play again")
                                 : qsTr("THE COMPUTER WINS!\nClick to try again"))
                              : qsTr("MOVE THE MOUSE TO CONTROL THE LEFT PADDLE\nCLICK TO START\nFirst to five points wins")
                        color: "#e9fff8"
                        font.bold: true
                        font.pixelSize: Math.max(13, court.height * 0.055)
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        wrapMode: Text.WordWrap
                    }
                }

                MouseArea {
                    id: gameControls
                    anchors.fill: parent
                    z: 11
                    hoverEnabled: true

                    onPositionChanged: {
                        if (rivetPongField.gameStarted && !rivetPongField.gameFinished) {
                            playerPaddle.y = Math.max(0,
                                Math.min(court.height - playerPaddle.height,
                                         mouse.y - playerPaddle.height / 2))
                        }
                    }

                    onClicked: {
                        if (rivetPongField.gameFinished) {
                            rivetPongField.resetGame()
                            rivetPongField.serve(1)
                        } else if (!rivetPongField.gameStarted) {
                            rivetPongField.serve(1)
                        }
                    }
                }
            }
        }
    }

    Timer {
        id: gameTimer
        interval: 16
        repeat: true
        running: presentation.activatedInCalamares
        onTriggered: rivetPongField.advanceGame()
    }

    function onActivate() {
        presentation.currentSlide = 0
    }

    function onLeave() {
        // API 2 stops the timer when Calamares leaves the slideshow.
    }
}
