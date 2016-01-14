#!/bin/bash
# plugin.sh - DevStack plugin for Heat

echo_summary "heat's plugin.sh was called..."
source $DEST/heat/devstack/lib/heat

if is_service_enabled h-eng h-api h-api-cfn h-api-cw; then
    if [[ "$1" == "stack" && "2" == "install" ]]; then
        echo_summary "Installing Heat"
        install_heatclient
        stack_install_service heat
        install_heat_other
        cleanup_heat

    elif [[ "$1" == "stack" && "2" == "post-config" ]]; then
        echo_summary "Configuring Heat"
        configure_heat

        if is_service_enabled key; then
            create_heat_accounts
        fi

    elif [[ "$1" == "stack" && "2" == "extra" ]]; then
        init_heat
        echo_summary "Starting Heat"
        start_heat
        if [ "$HEAT_BUILD_PIP_MIRROR" = "True" ]; then
            echo_summary "Building Heat pip mirrror"
            build_heat_pip_mirror
        fi 
    fi
    
    if [[ "$1" == "unstack" ]]; then
        echo_summary "Stopping Heat"
        stop_heat
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "Cleaning Heat"
        cleanup_heat
    fi
fi
