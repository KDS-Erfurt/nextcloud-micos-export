/**
 * JetBrains Space Automation
 * This Kotlin script file lets you automate build activities
 * For more info, see https://www.jetbrains.com/help/space/automation.html
 */

job("Build and publish Package") {
    startOn {
        gitPush {
            anyBranchMatching {
                +"release/*"
            }
        }
    }

    // download python image
    container(displayName = "Python", image = "python:3.9-bookworm") {
        // run python script
        shellScript {
            content = """
                echo "----- Install pdm -----"
                if pip install pdm; then
                    echo "----- pdm installed -----"
                else
                    echo "----- pdm installation failed -----"
                    exit 1
                fi
                
                echo "----- Build package -----"
                if pdm build; then
                    echo "----- Package build success -----"
                else
                    echo "----- Package build failed -----"
                    exit 1
                fi
                
                echo "----- Publish package to space -----"
                if pdm publish --no-build --repository https://pypi.pkg.jetbrains.space/bastelquartier/p/kds/python/legacy --username ${'$'}JB_SPACE_CLIENT_ID --password ${'$'}JB_SPACE_CLIENT_SECRET; then
                    echo "----- Package publish success -----"
                else
                    echo "----- Package publish failed -----"
                    exit 1
                fi
                                                                
                echo "----- Done -----"
            """.trimIndent()
        }
    }
}
