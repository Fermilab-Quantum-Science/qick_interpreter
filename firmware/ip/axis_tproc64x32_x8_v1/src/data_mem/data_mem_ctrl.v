// Control arbiter for memory access operations.
//
// The block arbitrates access to the memory. While executing
// either AXIS Read or Write, busy flag is asserted. If the 
// busy flag is not asserted, memory can be accessed using
// single mode (external block).
//
// MODE_REG:
// * 0 : AXIS Read (from memory to m_axis).
// * 1 : AXIS Write (from s_axis to memory).
//
// START_REG:
// * 0 : Stop.
// * 1 : Execute Operation.
module data_mem_ctrl (
	// Reset and clock.
	aclk_i			,
	aresetn_i		,

	// Selector.
	sel_o			,

	// axis_read handshake.
	ar_exec_o		,
	ar_exec_ack_i	,

	// axis_write handshake.
	aw_exec_o		,
	aw_exec_ack_i	,

	// Busy flag.
	busy_o			,

	// Registers.
	MODE_REG		,
	START_REG		
);

// Parameters.
parameter N = 16;

// Ports.
input			aclk_i;
input 			aresetn_i;
output	[1:0]	sel_o;
output			ar_exec_o;
input			ar_exec_ack_i;
output			aw_exec_o;
input			aw_exec_ack_i;
output			busy_o;
input			MODE_REG;
input			START_REG;

// States.
localparam	INIT_ST 			= 0;
localparam	AXIS_READ_ST 		= 1;
localparam	AXIS_READ_ACK_ST 	= 2;
localparam	AXIS_WRITE_ST 		= 3;
localparam	AXIS_WRITE_ACK_ST 	= 4;
localparam	END_ST				= 6;

// State register.
reg [2:0]	state;

// State flags.
reg			busy_int;
reg			ar_exec_int;
reg			aw_exec_int;
reg	[1:0]	sel_int;	// 0: single, 1: axis_read, 2: axis_write.

// Registers.
always @(posedge aclk_i) begin
	if (~aresetn_i) begin
		// State register.
		state	<= INIT_ST;
	end
	else begin
		// State register.
		case(state)
			INIT_ST:
				if (START_REG == 1'b1)
					if (MODE_REG == 1'b0)
						// AXIS read (from memory to m_axis).
						state <= AXIS_READ_ST;
					else
						// AXIS write (from s_axis to memory).
						state <= AXIS_WRITE_ST;

			AXIS_READ_ST:
				state <= AXIS_READ_ACK_ST;

			AXIS_READ_ACK_ST:
				if (ar_exec_ack_i == 1'b1)
					state <= END_ST;

			AXIS_WRITE_ST:
				state <= AXIS_WRITE_ACK_ST;

			AXIS_WRITE_ACK_ST:
				if (aw_exec_ack_i == 1'b1)
					state <= END_ST;

			END_ST:
				if (START_REG == 1'b0)
					state <= INIT_ST;
		endcase	
					
	end
end 

// FSM outputs.
always @(state) begin
	// Default.
	busy_int		= 0;
	ar_exec_int		= 0;
	aw_exec_int		= 0;
	sel_int			= 0;

	case (state)
		//INIT_ST:

		AXIS_READ_ST: begin
			busy_int		= 1;
			sel_int			= 1;
		end

		AXIS_READ_ACK_ST: begin
			ar_exec_int		= 1;
			busy_int		= 1;
			sel_int			= 1;
		end

		AXIS_WRITE_ST: begin
			busy_int		= 1;
			sel_int			= 2;
		end

		AXIS_WRITE_ACK_ST: begin
			aw_exec_int		= 1;
			busy_int		= 1;
			sel_int			= 2;
		end

		//END_ST:

	endcase
end

// Assign outputs.
assign sel_o		= sel_int;
assign ar_exec_o	= ar_exec_int;
assign aw_exec_o	= aw_exec_int;
assign busy_o		= busy_int;

endmodule

