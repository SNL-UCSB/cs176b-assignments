BMV2_SWITCH_EXE = simple_switch_grpc

BUILD_DIR = build
LOG_DIR = logs
P4_PROG = switch

P4C = p4c-bm2-ss
P4C_ARGS += --p4runtime-files $(BUILD_DIR)/$(P4_PROG).p4.p4info.txt

#RUN_SCRIPT = ./run_exercise.py
RUN_SCRIPT = ./start_mininet.py
TOPO = topology.json

source = $(P4_PROG).p4
compiled_json := $(source:.p4=.json)

# Set BMV2_SWITCH_EXE to override the BMv2 target
ifdef BMV2_SWITCH_EXE
run_args += -b $(BMV2_SWITCH_EXE)
endif

all: run

run: build
	sudo python $(RUN_SCRIPT)

stop:
	sudo mn -c

build: dirs $(compiled_json)

%.json: %.p4
	$(P4C) --p4v 16 $(P4C_ARGS) -o $(BUILD_DIR)/$@ $<

dirs:
	mkdir -p $(BUILD_DIR) $(LOG_DIR)

clean: stop
	rm -f *.pcap
	rm -rf $(BUILD_DIR) $(LOG_DIR)
	rm -f *.pyc
	rm -f *~
	rm -f *-runtime.json
