#!/usr/bin/python3 -OO
# Copyright 2007-2022 The SABnzbd-Team <team@sabnzbd.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

##############################################################################
# Decorators
##############################################################################
from typing import Union, Callable
from threading import Lock, RLock, Condition


# All operations that modify the queue need to happen in a lock
# Also used when importing NZBs to prevent IO-race conditions
# Names of wrapper-functions should be the same in misc.caller_name
# The NzbQueueLocker both locks and notifies the Downloader
NZBQUEUE_LOCK = RLock()
DOWNLOADER_CV = Condition(NZBQUEUE_LOCK)


def synchronized(lock: Union[Lock, RLock]):
    def wrap(func: Callable):
        def call_func(*args, **kw):
            # Using the try/finally approach is 25% faster compared to using "with lock"
            try:
                lock.acquire()
                return func(*args, **kw)
            finally:
                lock.release()

        return call_func

    return wrap


def NzbQueueLocker(func: Callable):
    global DOWNLOADER_CV

    def call_func(*params, **kparams):
        DOWNLOADER_CV.acquire()
        try:
            return func(*params, **kparams)
        finally:
            DOWNLOADER_CV.notify_all()
            DOWNLOADER_CV.release()

    return call_func
