# -*- coding:utf-8 -*-
"""
Author: GanLin
"""
__license__ = """
Copyright 2016 TeamSun, Inc.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""
version= "collector version 1.1"

import sys
import os
import traceback
import platform
import signal
import yaml
import pickle
from optparse import OptionParser
from com.teamsun.report.service import RunInfo
from com.teamsun.report.service.ConfigReader import read
from com.teamsun.report.service.LogReporter import LogListener
import pdb

def main():
    parser = OptionParser()
    parser.add_option("-d",dest="start_date",
                    help='start_date')
    parser.add_option("-c", dest="conf",help="conf")
    (option,args) = parser.parse_args()
    if option.start_date:
        start_date = option.start_date
    else:
        start_date = None
    collector_path = os.path.abspath('.')
    file_name = option.conf
    if not os.path.exists(file_name):
        print('Not exists conf file')
        exit(1)
    # 初始化运行信息输出组件
    try:
        confParser = yaml.load(file(file_name))
        if 'Windows' in platform.system():
            outer = RunInfo.InfoOuter('c:/xxx/report.txt', confParser)
        else:
            infoOutPath = confParser['base']['infoOutPath']  # Collector的日志文件路径
            outer = RunInfo.InfoOuter(infoOutPath, confParser)
        RunInfo.outer = outer
        RunInfo.out = outer.out
    except:
        print('InfoOuter init error')
        print(traceback.format_exc())
        exit(1)
    RunInfo.out.info(version)
    # 设置Agent所在目录
    try:
        sys.path.append(confParser['base']['agentPath'])
    except:
        RunInfo.out.fatal('Initialization fatal error.')
        RunInfo.out.fatal(traceback.format_exc())
        exit(1)
    conf =read(confParser,file_name)
    log_listener = LogListener(conf, RunInfo.out,collector_path,start_date=start_date)

    def signalHandler(signal, frame):
        try:
            RunInfo.out.info('App exit signal:' + str(signal))
            log_listener.isRun = False
            if log_listener.writingOffset:
                with open(log_listener.conf['readOffsetFile'], 'w') as writer:
                    pickle.dump(log_listener.readOffset, writer)
        except:
            RunInfo.out.error(traceback.format_exc())
        finally:
            log_listener.close()
            RunInfo.out.info('App exit.')
    try:
        signal.signal(signal.SIGTERM, signalHandler)
        signal.signal(signal.SIGINT, signalHandler)
        log_listener.startListen()
    except:
        RunInfo.out.fatal('LogCollector stop.')
        RunInfo.out.fatal(traceback.format_exc())

if __name__ == "__main__":
    main()
