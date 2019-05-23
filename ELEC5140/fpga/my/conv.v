`timescale 1ns / 1ps

module conv(
    	input clk,
    	input reset,
    	input [7:0] pxl_in,
			
	output [15:0] reg_00, output [15:0] reg_01, output [15:0] reg_02, output[15:0] sr_0, 	
	output [15:0] reg_10, output [15:0] reg_11, output [15:0] reg_12, output[15:0] sr_1, 
	output [15:0] reg_20, output [15:0] reg_21, output [15:0] reg_22, 
    	output [15:0] pxl_out,
		
	output valid
    );

	//Define constants
	parameter N = 5;	//Image columns
	parameter M = 5;	//Image rows
	parameter K = 3; 	//Kernel size

	// Intermediate wires
	wire [15:0] wire_00; wire [15:0] wire_01; wire [15:0] wire_02;
	wire [15:0] wire_10; wire [15:0] wire_11; wire [15:0] wire_12;
	wire [15:0] wire_20; wire [15:0] wire_21; wire [15:0] wire_22;

	// 3*3 kernel
	integer kernel_00 = 1; integer kernel_01 = 2; integer kernel_02 = 1;
	integer kernel_10 = 0; integer kernel_11 = 0; integer kernel_12 = 0;
	integer kernel_20 = 1; integer kernel_21 = 2; integer kernel_22 = 1;	

	// Row : 1
	mac mac_00(pxl_in, kernel_00, 0, wire_00);
	register r_00(clk, reset, wire_00, reg_00); 
	
	mac mac_01(pxl_in, kernel_01, reg_00, wire_01); 
	register r_01(clk, reset, wire_01, reg_01); 

	mac mac_02(pxl_in, kernel_02, reg_01, wire_02); 
	register r_02(clk, reset, wire_02, reg_02); 

	shift row_1(clk, reg_02, sr_0);

	// Row : 2
	mac mac_10(pxl_in, kernel_10, sr_0, wire_10); 
	register r_10(clk, reset, wire_10, reg_10); 

	mac mac_11(pxl_in, kernel_11, reg_10, wire_11); 
	register r_11(clk, reset, wire_11, reg_11); 

	mac mac_12(pxl_in, kernel_12, reg_11, wire_12); 
	register r_12(clk, reset, wire_12, reg_12); 

	shift row_2(clk, reg_12, sr_1);

	// Row : 3
	mac mac_20(pxl_in, kernel_20, sr_1, wire_20); 
	register r_20(clk, reset, wire_20, reg_20); 

	mac mac_21(pxl_in, kernel_21, reg_20, wire_21); 
	register r_21(clk, reset, wire_21, reg_21); 

	mac mac_22(pxl_in, kernel_22, reg_21, wire_22); 
	register r_22(clk, reset, wire_22, reg_22); 
	
	assign pxl_out = reg_22;	

	// Valid bit logic

	reg [8:0] counter = 0;
	reg temp = 0;

	always @(posedge clk) begin
		counter = counter + 1;
	
		// The logic below needs some revisiting to scale properly
		if (counter > ((K-1)*N + (K-1)) && counter < (M*N) + (K-1)) begin
			if ((counter - (K-1)) % N > 1) begin
				temp <= 1;
				end
			else
				temp <= 0;
				end
		else
			temp <= 0; 
			end
				 
	assign valid = temp;

endmodule

module mac(
    input [7:0] in,
    input [7:0] w,
    input [7:0] b,
    output [15:0] out
    );

wire [15:0] d;
assign d = w * in;
assign out = d + b;
 
endmodule

module shift
(
  input clk,
  input [15:0] data_in,
  output [15:0] data_out
);

// Depth = D = n-k; for now assume n to be 5
parameter D = 2;

// Define holding register for each bit
reg [D-1:0] hr_0; reg [D-1:0] hr_1; reg [D-1:0] hr_2; reg [D-1:0] hr_3;
reg [D-1:0] hr_4; reg [D-1:0] hr_5; reg [D-1:0] hr_6; reg [D-1:0] hr_7;
reg [D-1:0] hr_8; reg [D-1:0] hr_9; reg [D-1:0] hr_10; reg [D-1:0] hr_11;
reg [D-1:0] hr_12; reg [D-1:0] hr_13; reg [D-1:0] hr_14; reg [D-1:0] hr_15;

always @ (posedge clk) begin
  hr_0 [D-1:0] <= {hr_0[D-2:0], data_in[0]};
  hr_1 [D-1:0] <= {hr_1[D-2:0], data_in[1]};
  hr_2 [D-1:0] <= {hr_2[D-2:0], data_in[2]};
  hr_3 [D-1:0] <= {hr_3[D-2:0], data_in[3]};
  hr_4 [D-1:0] <= {hr_4[D-2:0], data_in[4]};
  hr_5 [D-1:0] <= {hr_5[D-2:0], data_in[5]};
  hr_6 [D-1:0] <= {hr_6[D-2:0], data_in[6]};
  hr_7 [D-1:0] <= {hr_7[D-2:0], data_in[7]};
  hr_8 [D-1:0] <= {hr_8[D-2:0], data_in[8]};
  hr_9 [D-1:0] <= {hr_9[D-2:0], data_in[9]};
  hr_10 [D-1:0] <= {hr_10[D-2:0], data_in[10]};
  hr_11 [D-1:0] <= {hr_11[D-2:0], data_in[11]};
  hr_12 [D-1:0] <= {hr_12[D-2:0], data_in[12]};
  hr_13 [D-1:0] <= {hr_13[D-2:0], data_in[13]};
  hr_14 [D-1:0] <= {hr_14[D-2:0], data_in[14]};
  hr_15 [D-1:0] <= {hr_15[D-2:0], data_in[15]};
end

assign data_out[0] = hr_0[D-1]; assign data_out[1] = hr_1[D-1];
assign data_out[2] = hr_2[D-1]; assign data_out[3] = hr_3[D-1];
assign data_out[4] = hr_4[D-1]; assign data_out[5] = hr_5[D-1];
assign data_out[6] = hr_6[D-1]; assign data_out[7] = hr_7[D-1];
assign data_out[8] = hr_8[D-1]; assign data_out[9] = hr_9[D-1];
assign data_out[10] = hr_10[D-1]; assign data_out[11] = hr_11[D-1];
assign data_out[12] = hr_12[D-1]; assign data_out[13] = hr_13[D-1];
assign data_out[14] = hr_14[D-1]; assign data_out[15] = hr_15[D-1];

endmodule
