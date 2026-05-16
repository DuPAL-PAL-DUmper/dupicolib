# dupicolib

## Introduction

This Python library contains the common code used by other tools to communicate with the DuPAL V3 "dupico" board, specifically command handling and pin mapping.

It also includes an experimental Brutus28 command adapter. Brutus28 uses a text command shell rather than the dupico binary protocol, so callers should select `Brutus28BoardCommands` explicitly instead of using dupico model autodetection.

## Requirements

This library requires Python >= 3.12
