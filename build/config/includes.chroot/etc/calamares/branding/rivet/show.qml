import QtQuick 2.5
import calamares.slideshow 1.0

Presentation {
    id: presentation
    mouseNavigation: false
    arrowNavigation: false
    keyShortcutsEnabled: false

    Slide {
        id: wikiSlide
        title: qsTr("Rivet Wiki")
        notes: qsTr("The story of Rivet Linux, what we learned, and what comes next.")

        Rectangle {
            anchors.fill: parent
            color: "#0b1720"
            radius: 12
            border.color: "#20c997"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 9

                Text {
                    text: "RIVET WIKI"
                    color: "#20c997"
                    font.bold: true
                    font.pixelSize: 29
                }
                Text {
                    text: "A small distro with a big journey."
                    color: "#dcecf3"
                    font.pixelSize: 18
                }
                Rectangle {
                    width: parent.width
                    height: 2
                    color: "#24404b"
                }

                Row {
                    id: wikiColumns
                    width: parent.width
                    height: parent.height - 92
                    spacing: 24

                    Flickable {
                        id: leftScroll
                        width: (wikiColumns.width - wikiColumns.spacing) / 2
                        height: wikiColumns.height
                        contentWidth: width
                        contentHeight: leftColumn.implicitHeight
                        clip: true
                        boundsBehavior: Flickable.StopAtBounds

                        Column {
                            id: leftColumn
                            width: leftScroll.width
                            spacing: 11

                            Text {
                                text: "WHERE IT STARTED"
                                color: "#60a5fa"
                                font.bold: true
                                font.pixelSize: 17
                            }
                            Text {
                                width: parent.width
                                text: "Rivet started with a simple goal: make a Linux system that feels like it belongs to the person using it. Debian became the foundation because reliable packages, a maintainable base and a real installer matter more than reinventing everything. XFCE gave us a light desktop to shape, and live-build lets us assemble repeatable images instead of rebuilding everything by hand."
                                color: "#e8f1f5"
                                font.pixelSize: 15
                                lineHeight: 1.18
                                wrapMode: Text.WordWrap
                            }
                            Text {
                                text: "BUILDING THE SYSTEM"
                                color: "#60a5fa"
                                font.bold: true
                                font.pixelSize: 17
                            }
                            Text {
                                width: parent.width
                                text: "The project grew its own visual identity: a blue-and-green logo, Chip the beaver, wallpapers, a branded Calamares installer, a welcome screen, a settings hub, a software store and tools such as Chip Fixs. The idea is to make common tasks easier without hiding Linux or taking control away from the person at the keyboard."
                                color: "#e8f1f5"
                                font.pixelSize: 15
                                lineHeight: 1.18
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    Flickable {
                        id: rightScroll
                        width: (wikiColumns.width - wikiColumns.spacing) / 2
                        height: wikiColumns.height
                        contentWidth: width
                        contentHeight: rightColumn.implicitHeight
                        clip: true
                        boundsBehavior: Flickable.StopAtBounds

                        Column {
                            id: rightColumn
                            width: rightScroll.width
                            spacing: 11

                            Text {
                                text: "WHAT WE LEARNED"
                                color: "#60a5fa"
                                font.bold: true
                                font.pixelSize: 17
                            }
                            Text {
                                width: parent.width
                                text: "We moved through several test images, from #100 and #101 to #102. We wrote build hooks, adjusted package lists, fixed launchers and added automated checks. We also learned that a green build only proves the checks that ran; it cannot prove that a real machine will always reach the desktop."
                                color: "#e8f1f5"
                                font.pixelSize: 15
                                lineHeight: 1.18
                                wrapMode: Text.WordWrap
                            }
                            Text {
                                text: "RELIABILITY FIRST"
                                color: "#60a5fa"
                                font.bold: true
                                font.pixelSize: 17
                            }
                            Text {
                                width: parent.width
                                text: "In #102, the custom startup animation failed during a real test and the system did not complete a normal desktop handoff. So we are removing the splash program and its custom integration, returning to visible Linux startup messages, trimming the live dock to essential apps, and replacing Rivet Pong with this wiki. Reliability comes before decoration."
                                color: "#e8f1f5"
                                font.pixelSize: 15
                                lineHeight: 1.18
                                wrapMode: Text.WordWrap
                            }
                            Text {
                                text: "WHAT COMES NEXT"
                                color: "#60a5fa"
                                font.bold: true
                                font.pixelSize: 17
                            }
                            Text {
                                width: parent.width
                                text: "Rivet is still pre-alpha. Next we must build a newly authorized image and verify BIOS and UEFI startup, installation to a virtual disk, first login, networking, audio, software updates and removal of live-only launchers. Each bug should become a test or a lesson documented for the next build."
                                color: "#e8f1f5"
                                font.pixelSize: 15
                                lineHeight: 1.18
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }

                Text {
                    text: "Build it, test it, learn from it, and make it better."
                    color: "#9eb7c3"
                    font.italic: true
                    font.pixelSize: 14
                }
            }
        }
    }

    function onActivate() {
        presentation.currentSlide = 0
    }
    function onLeave() {
    }
}
